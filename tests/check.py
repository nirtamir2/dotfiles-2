#!/usr/bin/env python3
"""Offline validation and integration tests using a disposable home directory."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import sys
ROOT = Path(__file__).resolve().parents[1]

def run(*args, ok=True):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if ok and result.returncode:
        raise AssertionError(f'{args}: {result.stderr}\n{result.stdout}')
    return result

for path in ['setup', 'bootstrap/installations', 'bootstrap/node', 'bootstrap/shell', 'bootstrap/links', 'bootstrap/homebrew', 'bootstrap/new-mac', 'bin/schnizvim', 'bin/dotfiles', 'bin/skills-explicit']:
    run('bash', '-n', str(ROOT/path))
for path in ['.zshrc','.zprofile','.zshenv','shell/aliases.zsh','shell/functions.zsh','shell/history.zsh','shell/navigation.zsh']:
    run('zsh', '-n', str(ROOT/path))
for path in [ROOT/'Brewfile', *sorted((ROOT/'packages').glob('Brewfile.*'))]:
    run('ruby', '-c', str(path))
for path in [ROOT/'docs/source-inventory.json']:
    json.loads(path.read_text())
with tempfile.TemporaryDirectory(prefix='dotfiles home ') as tmp:
    home = Path(tmp)
    def manage(command, *args, ok=True):
        return run(sys.executable, str(ROOT/'bootstrap/manage.py'), command, '--target', tmp, *args, ok=ok)
    storage = home/'Library/Application Support/Code/User/globalStorage/storage.json'
    storage.parent.mkdir(parents=True)
    storage.write_text(json.dumps({'userDataProfiles':[{'name':'Cursor Default','location':'custom-id'}]}))
    original = home/'.zshrc'
    original.write_text('original shell\n')
    before = list(home.iterdir())
    manage('plan')
    assert list(home.iterdir()) == before, 'plan must not create files'
    assert manage('link',ok=False).returncode != 0
    assert original.read_text() == 'original shell\n'
    assert list(home.iterdir()) == before, 'conflict preflight must be atomic'
    manage('link','--replace')
    assert original.is_symlink()
    assert not (home/'Library/Application Support/Code/User/profiles/custom-id/keybindings.json').exists(), 'core leaves VS Code alone'
    journals = list((home/'.local/state/dotfiles/backups').glob('*/manifest.json'))
    assert len(journals) == 1
    manage('link')
    assert len(list((home/'.local/state/dotfiles/backups').glob('*/manifest.json'))) == 1
    # Restore cannot silently overwrite new user work.
    original.unlink(); original.write_text('new user work\n')
    assert run(sys.executable,str(ROOT/'bootstrap/manage.py'),'restore',str(journals[0]),ok=False).returncode != 0
    assert original.read_text() == 'new user work\n'
    original.unlink(); original.symlink_to(ROOT/'.zshrc')
    run(sys.executable,str(ROOT/'bootstrap/manage.py'),'restore',str(journals[0]))
    assert not original.is_symlink() and original.read_text() == 'original shell\n'
    assert not (home/'.dotfiles').exists()
    run(sys.executable,str(ROOT/'bootstrap/manage.py'),'restore',str(journals[0]))
    # Never write through an unrelated parent symlink.
    foreign = home/'foreign';foreign.mkdir()
    (home/'.config').symlink_to(foreign, target_is_directory=True)
    assert manage('link','--profile','vim',ok=False).returncode != 0
    assert list(foreign.iterdir()) == []
    (home/'.config').unlink()
    manage('link','--profile','all','--replace')
    assert (home/'.config/schnizvim').is_symlink()
    assert (home/'Library/Application Support/Code/User/profiles/custom-id/keybindings.json').is_symlink()
    assert not (home/'.config/karabiner').exists()
    assert not (home/'.config/nvim').exists(), 'existing Neovim namespace stays independent'
# Cancellation must not turn an empty selection into a global package upgrade.
with tempfile.TemporaryDirectory(prefix='dotfiles tools ') as tmp:
    folder = Path(tmp)
    (folder/'brew').write_text('#!/bin/bash\necho "$*" >> "$TEST_LOG"\necho "{}"\n')
    (folder/'jq').write_text('#!/bin/bash\ncat >/dev/null\nprintf "git\\t1\\t2\\n"\n')
    (folder/'fzf').write_text('#!/bin/bash\ncat >/dev/null\nexit 130\n')
    for path in folder.iterdir(): path.chmod(0o755)
    env = {**os.environ, 'PATH': tmp+':/usr/bin:/bin', 'TEST_LOG':str(folder/'log')}
    result = subprocess.run([str(ROOT/'bin/brew-interactive')], env=env, capture_output=True)
    assert result.returncode == 0
    assert (folder/'log').read_text() == 'outdated --json\n'
    (folder/'fzf').write_text('#!/bin/bash\ncat\n')
    result = subprocess.run([str(ROOT/'bin/brew-interactive')], env=env, capture_output=True)
    assert result.returncode == 0
    assert (folder/'log').read_text().endswith('upgrade git\n')

# The offline guide must build identically and contain no broken local navigation.
from html.parser import HTMLParser
class GuideLinks(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set()
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs: self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs: self.links.append(attrs['href'])
before=(ROOT/'guide/index.html').read_bytes()
run(sys.executable, str(ROOT/'guide/build.py'))
assert (ROOT/'guide/index.html').read_bytes() == before
links=GuideLinks(); links.feed(before.decode())
for link in links.links:
    if link.startswith('#'): assert link[1:] in links.ids, link
    elif not link.startswith(('https://','http://')): assert (ROOT/'guide'/link).exists(), link
run(sys.executable, str(ROOT/'tests/new_mac.py'))
run('node', '--check', 'bootstrap/skills/skills.mjs')
run('node', '--test', 'bootstrap/skills/skills.test.mjs')
print('PASS: new-Mac restore tests, skill invocation policy, syntax, data, link/restore integration, profile discovery, symlink boundaries, Homebrew cancellation, offline guide.')
