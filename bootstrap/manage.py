#!/usr/bin/env python3
"""Explicit links, preflight, reversible backup journal; never traverse target symlink directories."""
import argparse
import datetime
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]


def manifest(profile, home):
    core = [('.', '.dotfiles'), ('.zprofile', '.zprofile'), ('.zshenv', '.zshenv'), ('.zshrc', '.zshrc'), ('.gitconfig', '.gitconfig'),
            ('.vimrc', '.vimrc'), ('.config/starship.toml', '.starship.toml'), ('.jq', '.jq'), ('.gitignore_global', '.gitignore_global'), ('.gitattributes', '.gitattributes'),
            ('bin', '.local/share/dotfiles/bin')]
    vscode = [('editors/vscode/settings.json', 'Library/Application Support/Code/User/settings.json'),
            ('editors/vscode/keybindings.json', 'Library/Application Support/Code/User/keybindings.json')]
    core += [(str(p.relative_to(ROOT)), p.name) for p in sorted((ROOT/'git-configs').glob('*.gitconfig'))]
    vscode += [(str(p.relative_to(ROOT)), 'Library/Application Support/Code/User/snippets/'+p.name)
             for p in sorted((ROOT/'editors/vscode/snippets').glob('*')) if p.is_file()]
    storage = home/'Library/Application Support/Code/User/globalStorage/storage.json'
    if profile in ('vscode', 'all') and storage.exists():
        profiles = json.loads(storage.read_text()).get('userDataProfiles', [])
        for item in profiles:
            location = item.get('location', '')
            if not location or '/' in location or location in ('.', '..'):
                continue
            source_dir = (ROOT/'editors/vscode/profiles'/item.get('name', '')).resolve()
            if not source_dir.is_relative_to(ROOT/'editors/vscode/profiles'):
                continue
            for name in ['settings.json', 'keybindings.json']:
                source = source_dir/name
                if source.is_file():
                    vscode.append((str(source.relative_to(ROOT)), 'Library/Application Support/Code/User/profiles/'+location+'/'+name))
            for source in sorted((source_dir/'snippets').glob('*')):
                if source.is_file():
                    vscode.append((str(source.relative_to(ROOT)), 'Library/Application Support/Code/User/profiles/'+location+'/snippets/'+source.name))
    groups = {'core': core, 'vim': [('.config/schnizvim', '.config/schnizvim')],
              'tmux': [('.config/tmux', '.config/tmux')],
              'vscode': vscode,
              'npm': [('.npmrc', '.npmrc')]}
    return sum(groups.values(), []) if profile == 'all' else groups[profile]


def exists(path):
    return os.path.lexists(path)


def same_link(target, source):
    return target.is_symlink() and target.resolve() == source.resolve()


def check_parents(target, home):
    parent = target.parent
    while parent != home:
        if parent.is_symlink():
            raise ValueError(f'Parent is a symlink: {parent}. Resolve this separately; no directory will be traversed.')
        if exists(parent) and not parent.is_dir():
            raise ValueError(f'Parent is not a directory: {parent}')
        parent = parent.parent


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2)+'\n')
    temp.replace(path)


def restore(path):
    journal = json.loads(path.read_text())
    home = Path(journal['home'])
    if journal.get('restored'):
        print('Already restored.'); return
    # Validate the whole operation before altering anything.
    for entry in journal['entries']:
        target, source = Path(entry['target']), Path(entry['source'])
        if not target.is_relative_to(home):
            raise ValueError('Invalid target outside home')
        check_parents(target, home)
        if exists(target) and not same_link(target, source):
            raise ValueError(f'Refusing to replace a file changed after linking: {target}')
        if entry['backup'] and not exists(Path(entry['backup'])):
            raise ValueError(f"Missing backup: {entry['backup']}")
    for entry in reversed(journal['entries']):
        target = Path(entry['target'])
        if target.is_symlink(): target.unlink()
        if entry['backup']: Path(entry['backup']).rename(target)
    journal['restored'] = True
    save(path, journal)
    print(f'Restored {len(journal["entries"])} paths. Empty parent directories may remain.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'link', 'status', 'restore'])
    parser.add_argument('backup', nargs='?')
    parser.add_argument('--profile', choices=['core','vim','tmux','vscode','npm','all'], default='core')
    parser.add_argument('--target', type=Path, default=Path.home(), help='Alternate home directory (for testing)')
    parser.add_argument('--replace', action='store_true', help='Back up conflicting files before replacing them')
    args = parser.parse_args()
    if args.command == 'restore':
        if not args.backup: parser.error('restore requires a manifest.json path')
        restore(Path(args.backup).resolve()); return
    if args.backup: parser.error('Unexpected positional argument')
    home = args.target.expanduser().resolve()
    entries = []
    conflicts = []
    for src, dst in manifest(args.profile, home):
        source, target = (ROOT/src).resolve(), home/dst
        if not source.exists(): raise ValueError(f'Missing source: {source}')
        check_parents(target, home)
        state = 'linked' if same_link(target, source) else ('conflict' if exists(target) else 'new')
        print(f'{state:8} ~/{dst} <- {src}')
        if state == 'linked': continue
        entries.append((source, target))
        if state == 'conflict': conflicts.append(str(target))
    if args.command != 'link': return
    if conflicts and not args.replace:
        raise ValueError('Conflicts found; no files changed. Review ./setup plan, then use --replace for timestamped backups.')
    if not entries:
        print('Everything is already linked.'); return
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    backup_dir = home/'.local/state/dotfiles/backups'/stamp
    check_parents(backup_dir/'manifest.json', home)
    backup_dir.mkdir(parents=True, mode=0o700)
    journal = {'home':str(home), 'root':str(ROOT), 'entries':[]}
    journal_path = backup_dir/'manifest.json'
    save(journal_path, journal)
    try:
        for index, (source, target) in enumerate(entries):
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = backup_dir/str(index) if exists(target) else None
            entry = {'source':str(source), 'target':str(target), 'backup':str(backup) if backup else None}
            if backup: target.rename(backup)
            journal['entries'].append(entry)
            save(journal_path, journal)
            target.symlink_to(source, target_is_directory=source.is_dir())
    except Exception:
        restore(journal_path)
        raise
    print(f'Linked {len(entries)} paths. Restore with: ./setup restore "{journal_path}"')


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
