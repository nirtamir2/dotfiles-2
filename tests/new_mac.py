#!/usr/bin/env python3
"""Exercise new-Mac restore paths with temporary homes and mocked app commands."""
import base64
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
import desktop
import editor
import doctor

# No installation command is invoked during dry-run; invalid options fail first.
result=subprocess.run([str(ROOT/'setup'),'install','--dry-run'],capture_output=True,text=True,check=True)
assert 'extras --apply' in result.stdout and 'core --replace' in result.stdout
result=subprocess.run([str(ROOT/'setup'),'install','--dry-run','--minimal','--skip-vscode','--skip-preferences'],capture_output=True,text=True,check=True)
assert 'extras --apply' not in result.stdout and 'editor.py' not in result.stdout and 'desktop.py' not in result.stdout
assert subprocess.run([str(ROOT/'setup'),'install','--unknown'],capture_output=True).returncode==2

class Defaults:
    def __init__(self):
        self.calls=[];self.busy=False
        self.original={'com.apple.dock':{'autohide':False,'unrelated':'keep'}}
    def __call__(self,args,**kwargs):
        self.calls.append(args)
        if args[0]=='pgrep':return SimpleNamespace(returncode=0 if self.busy else 1,stdout=b'')
        if args[1]=='export':return SimpleNamespace(returncode=0,stdout=plistlib.dumps(self.original.get(args[2],{})))
        return SimpleNamespace(returncode=0,stdout=b'')

with tempfile.TemporaryDirectory(prefix='new-mac-desktop-') as tmp:
    home=Path(tmp);fake=Defaults()
    desktop.apply(home,False,fake)
    assert list(home.iterdir())==[] and not fake.calls, 'desktop preview must not read/write system preferences'
    desktop.apply(home,True,fake)
    warp=home/'.warp/settings.toml';assert '__DOTFILES_HOME__' not in warp.read_text()
    theme=home/'.warp/themes/standard/classic_vivid.yaml';assert theme.is_file()
    backups=list((home/'.local/state/dotfiles/preferences').glob('*.json'));assert len(backups)==1
    data=json.loads(backups[0].read_text());assert data['domains']['com.apple.dock']['autohide']=={'existed':True,'value':False}
    assert 'unrelated' not in data['domains']['com.apple.dock']
    assert backups[0].stat().st_mode & 0o077 == 0
    assert any(c[:4]==['defaults','write','com.blackbeltlabs.Zappy','selectScreenArea'] and c[4]=='-data' for c in fake.calls)
    assert not any(any(x in c for x in ['access_token','email','userID','items']) for c in fake.calls)
    warp.write_text('user changed theme\n');fake.busy=True;fake.calls=[]
    skipped=desktop.apply(home,True,fake)
    assert set(skipped)==set(desktop.APP_DOMAINS)
    assert warp.read_text()=='user changed theme\n'
    assert not any(c[0]=='defaults' and c[1]=='write' and c[2] in desktop.APP_DOMAINS for c in fake.calls)
    fake.busy=False;fake.calls=[];desktop.restore(backups[0],fake)
    assert ['defaults','write','com.apple.dock','autohide','-bool','false'] in fake.calls
    assert ['defaults','delete','com.apple.dock','show-recents'] in fake.calls
    assert not any('unrelated' in c for c in fake.calls)
with tempfile.TemporaryDirectory(prefix='new-mac-system-only-') as tmp:
    home=Path(tmp);fake=Defaults()
    desktop.apply(home,True,fake,system_only=True)
    assert not (home/'.warp').exists()
    assert not any(c[0]=='defaults' and c[1]=='write' and c[2] in desktop.APP_DOMAINS for c in fake.calls)

# Dictation shares a nested dictionary with every system shortcut. Applying and
# restoring it must preserve unrelated entries, including later user edits.
class ShortcutDefaults(Defaults):
    domain = 'com.apple.symbolichotkeys'
    def __call__(self, args, **kwargs):
        result = super().__call__(args, **kwargs)
        if args[:3] == ['defaults', 'write', self.domain]:
            self.original.setdefault(self.domain, {})[args[3]] = plistlib.loads(args[4].encode())
        elif args[:3] == ['defaults', 'delete', self.domain]:
            self.original.setdefault(self.domain, {}).pop(args[3], None)
        return result

for existing in [True, False]:
    with tempfile.TemporaryDirectory(prefix='new-mac-dictation-') as tmp:
        home=Path(tmp);fake=ShortcutDefaults()
        old={'enabled':False,'value':{'type':'modifier','parameters':[17,19]}}
        if existing:
            fake.original[fake.domain]={'AppleSymbolicHotKeys':{'164':old,'175':{'enabled':True}},'other':'keep'}
        desktop.apply(home,True,fake,system_only=True)
        entries=fake.original[fake.domain]['AppleSymbolicHotKeys']
        assert entries['164']['value']['parameters']==[1048592,18446744073708503023]
        assert type(entries['164']['enabled']) is bool
        if existing:
            assert entries['175']=={'enabled':True} and fake.original[fake.domain]['other']=='keep'
        backup=next((home/'.local/state/dotfiles/preferences').glob('*.json'))
        saved=json.loads(backup.read_text())['domains'][fake.domain]['AppleSymbolicHotKeys']
        assert set(saved['dict_entries'])=={'164'}, 'backup must not capture unrelated shortcuts'
        entries['175']={'enabled':False,'userEdited':True}
        desktop.restore(backup,fake)
        restored=fake.original[fake.domain]['AppleSymbolicHotKeys']
        assert restored['175']=={'enabled':False,'userEdited':True}
        if existing: assert restored['164']==old
        else: assert '164' not in restored

# Restoring an originally absent shortcut dictionary removes the empty key.
with tempfile.TemporaryDirectory(prefix='new-mac-dictation-empty-') as tmp:
    home=Path(tmp);fake=ShortcutDefaults()
    desktop.apply(home,True,fake,system_only=True)
    desktop.restore(next((home/'.local/state/dotfiles/preferences').glob('*.json')),fake)
    assert 'AppleSymbolicHotKeys' not in fake.original[fake.domain]

with tempfile.TemporaryDirectory(prefix='new-mac-defaults-failure-') as tmp:
    home=Path(tmp);fake=Defaults()
    def failing(args,**kwargs):
        if args[:4]==['defaults','write','com.apple.dock','autohide']:
            return SimpleNamespace(returncode=1,stdout=b'')
        return fake(args,**kwargs)
    try:desktop.apply(home,True,failing)
    except ValueError as error:assert 'Restore saved keys' in str(error)
    else:raise AssertionError('failed preference write must surface a recovery command')
    assert len(list((home/'.local/state/dotfiles/preferences').glob('*.json')))==1
with tempfile.TemporaryDirectory(prefix='new-mac-symlink-') as tmp:
    home=Path(tmp);outside=home/'outside';outside.mkdir();(home/'.warp').symlink_to(outside)
    try:desktop.apply(home,True,Defaults())
    except ValueError:pass
    else:raise AssertionError('must refuse a symlinked parent')
    assert list(outside.iterdir())==[]

with tempfile.TemporaryDirectory(prefix='new-mac-editor-') as tmp:
    home=Path(tmp);calls=[]
    first=(editor.PROFILE/'extensions.txt').read_text().splitlines()[0]
    def code(args,**kwargs):
        calls.append(args)
        if '--list-extensions' in args:return SimpleNamespace(stdout='',returncode=0)
        return SimpleNamespace(stdout='',returncode=1 if args[-1]==first else 0)
    editor.seed(home,False,code,sys.executable);assert list(home.iterdir())==[]
    result=editor.seed(home,True,code,sys.executable)
    assert result['failed_extensions']==[first]
    settings=home/'Library/Application Support/Code/User/settings.json'
    assert settings.read_bytes()==(editor.PROFILE/'settings.json').read_bytes()
    settings.write_text('{"userEdited":true}\n');editor.seed(home,True,code,sys.executable)
    assert 'userEdited' in settings.read_text(), 'rerun must preserve user edits'
    assert 'VS Code extensions needing retry' in doctor.audit(home)
with tempfile.TemporaryDirectory(prefix='existing-editor-') as tmp:
    home=Path(tmp);settings=home/'Library/Application Support/Code/User/settings.json';settings.parent.mkdir(parents=True);settings.write_text('existing')
    def forbidden(*args,**kwargs):raise AssertionError('existing editor must not install extensions')
    result=editor.seed(home,True,forbidden,sys.executable)
    assert result['preserved_existing'] and settings.read_text()=='existing'
    assert not (home/'.local').exists()
print('PASS: installer plans, fresh/existing VS Code, failed extensions, desktop preservation, key backups/restore, running-app skips and symlink boundaries.')
