#!/usr/bin/env python3
"""Seed portable app files and allowlisted macOS preferences; never import app databases."""
import argparse
import base64
import datetime
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import uuid
from manage import check_parents

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'preferences/desktop'
APP_DOMAINS = {'com.superultra.Homerow': 'Homerow', 'com.blackbeltlabs.Zappy': 'Zappy'}


def run(args, **kwargs):
    return subprocess.run(args, capture_output=True, **kwargs)


def value_args(value):
    if isinstance(value, bool): return ['-bool', str(value).lower()]
    if isinstance(value, int): return ['-int', str(value)]
    if isinstance(value, float): return ['-float', str(value)]
    if isinstance(value, str): return ['-string', value]
    if isinstance(value, bytes): return ['-data', value.hex()]
    if isinstance(value, dict) and set(value) == {'data_base64'}:
        return ['-data', base64.b64decode(value['data_base64'], validate=True).hex()]
    if isinstance(value, (list, dict)):
        # XML preserves nested types and unsigned shortcut masks exactly.
        return [plistlib.dumps(value, fmt=plistlib.FMT_XML).decode()]
    raise ValueError('Unsupported preference value; add a reviewed type handler first')


def dictionary_entries(value):
    """A reviewed patch to selected entries, rather than a whole dictionary."""
    return isinstance(value, dict) and set(value) == {'dict_entries'}


def preference_dictionary(value):
    if not isinstance(value, dict):
        raise ValueError('Expected a preference dictionary; refusing to replace another type')
    return value.copy()


def read_domain(domain, runner=run):
    result = runner(['defaults', 'export', domain, '-'])
    return plistlib.loads(result.stdout) if result.returncode == 0 else {}


def seed_file(target, content, home, apply):
    check_parents(target, home)
    if os.path.lexists(target):
        print(f'Preserved existing {target}')
        return 'preserved'
    print(f'Seed {target}')
    if apply:
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation protects against a file appearing after preflight.
        with target.open('xb') as file: file.write(content)
    return 'created'


def restore(path, runner=run):
    journal = json.loads(path.read_text())
    for domain, saved in journal['domains'].items():
        if domain in APP_DOMAINS and runner(['pgrep', '-x', APP_DOMAINS[domain]]).returncode == 0:
            raise ValueError(f'Quit {APP_DOMAINS[domain]} before restoring preferences')
    for domain, saved in journal['domains'].items():
        for key, prior in saved.items():
            if 'dict_entries' in prior:
                current = preference_dictionary(read_domain(domain, runner).get(key, {}))
                for entry, previous in prior['dict_entries'].items():
                    if previous['existed']: current[entry] = previous['value']
                    else: current.pop(entry, None)
                command = (['defaults', 'write', domain, key, *value_args(current)]
                           if current or prior['existed'] else ['defaults', 'delete', domain, key])
            else:
                command = ['defaults', 'write', domain, key, *value_args(prior['value'])] if prior['existed'] else ['defaults', 'delete', domain, key]
            result = runner(command)
            if result.returncode and (prior['existed'] or command[1] == 'write'):
                raise ValueError(f'Could not restore {domain}: {key}')
    print('Restored saved keys. Reopen apps/log out for cached settings to refresh.')


def apply(home, execute=False, runner=run, system_only=False):
    if not system_only:
        settings = (SOURCE/'warp-settings.toml.in').read_text().replace('__DOTFILES_HOME__', json.dumps(str(home))[1:-1])
        seed_file(home/'.warp/settings.toml', settings.encode(), home, execute)
        seed_file(home/'.warp/themes/standard/classic_vivid.yaml', (SOURCE/'warp-themes/classic_vivid.yaml').read_bytes(), home, execute)
        for relative in ['gh/config.yml', 'gh-dash/config.yml', 'gnupg/gpg.conf', 'gnupg/gpg-agent.conf']:
            target = home/('.'+relative if relative.startswith('gnupg/') else '.config/'+relative)
            if execute and relative.startswith('gnupg/') and not target.parent.exists():
                check_parents(target, home)
                target.parent.mkdir(mode=0o700)
            state = seed_file(target, (SOURCE/relative).read_bytes(), home, execute)
            if execute and relative.startswith('gnupg/') and state == 'created': target.chmod(0o600)
    domains = json.loads((ROOT/'preferences/macos.json').read_text())
    for domain in ([] if system_only else APP_DOMAINS):
        domains[domain] = json.loads((SOURCE/(domain+'.json')).read_text())
    journal = {'domains': {}}
    skipped = []
    backup = home/'.local/state/dotfiles/preferences'/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json')
    for domain, values in domains.items():
        # Validate before any domain mutation.
        for value in values.values():
            if dictionary_entries(value):
                value_args(preference_dictionary(value['dict_entries']))
            else: value_args(value)
        if execute and domain in APP_DOMAINS and runner(['pgrep','-x',APP_DOMAINS[domain]]).returncode == 0:
            skipped.append(domain)
            print(f'Skipped {domain}: quit {APP_DOMAINS[domain]} and rerun ./setup desktop --apply')
            continue
        print(f'{"Apply" if execute else "Plan"} {domain}: {len(values)} reviewed preference keys')
        if not execute: continue
        current = read_domain(domain, runner)
        saved = {}
        writes = {}
        for key, desired in values.items():
            value = current.get(key)
            if dictionary_entries(desired):
                entries = preference_dictionary(value if key in current else {})
                saved[key] = {'existed': key in current, 'dict_entries': {
                    entry: {'existed': entry in entries, 'value': entries.get(entry)}
                    for entry in desired['dict_entries']}}
                entries.update(desired['dict_entries'])
                writes[key] = entries
                continue
            if isinstance(value, bytes): value = {'data_base64':base64.b64encode(value).decode()}
            saved[key] = {'existed': key in current, 'value': value}
            writes[key] = desired
        journal['domains'][domain] = saved
        check_parents(backup, home)
        backup.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with backup.open('w') as file:
            os.chmod(backup, 0o600); json.dump(journal, file, indent=2)
        for key, value in writes.items():
            result = runner(['defaults','write',domain,key,*value_args(value)])
            if result.returncode:
                raise ValueError(f'Failed {domain}: {key}. Restore saved keys with ./setup desktop --restore {backup}')
    if execute:
        state = home/'.local/state/dotfiles/desktop.json'
        if not system_only:
            state.write_text(json.dumps({'skipped_domains':skipped,'backup':str(backup) if journal['domains'] else None},indent=2)+'\n')
        print('Preferences saved; reopen apps or log out to refresh cached UI preferences.')
        if journal['domains']: print(f'Restore preference keys: ./setup desktop --restore {backup}')
    return skipped


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--restore', type=Path)
    parser.add_argument('--system-only',action='store_true',help='Only apply preferences/macos.json, without app files/preferences')
    args=parser.parse_args()
    if args.apply or args.restore:
        if sys.platform != 'darwin': parser.error('Preference writes require macOS')
    if args.restore: restore(args.restore)
    else: apply(Path.home(), args.apply, system_only=args.system_only)

if __name__ == '__main__':
    try: main()
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr); sys.exit(1)
