#!/usr/bin/env python3
"""Seed a fresh VS Code default profile from Nir's current coding profile."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from manage import check_parents

ROOT=Path(__file__).resolve().parents[1]
PROFILE=ROOT/'editors/vscode/profiles/Cursor Default'


def seed(home, execute=False, runner=subprocess.run, code=None):
    target=home/'Library/Application Support/Code/User'
    state=home/'.local/state/dotfiles/vscode.json'
    sources={PROFILE/'settings.json':target/'settings.json',PROFILE/'keybindings.json':target/'keybindings.json'}
    sources.update({p:target/'snippets'/p.name for p in (PROFILE/'snippets').glob('*') if p.is_file()})
    owned=state.exists() and json.loads(state.read_text()).get('seeded') is True
    existing=any(os.path.lexists(p) for p in sources.values()) or (target/'globalStorage/storage.json').exists() or (target/'profiles').exists()
    if existing and not owned:
        print('Preserved existing VS Code configuration. Import a saved .code-profile manually if desired.')
        return {'seeded':False,'preserved_existing':True,'failed_extensions':[]}
    for src,dst in sources.items():
        check_parents(dst,home)
        if not os.path.lexists(dst):
            print(f'Seed VS Code {dst.relative_to(target)} from Cursor Default')
            if execute:
                dst.parent.mkdir(parents=True,exist_ok=True)
                with dst.open('xb') as file:file.write(src.read_bytes())
    if not execute:
        print('Install saved Cursor Default extension IDs into the fresh default profile. Existing named profiles stay untouched.')
        return {'seeded':False,'preserved_existing':False,'failed_extensions':[]}
    check_parents(state,home);state.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    result={'seeded':True,'preserved_existing':False,'failed_extensions':[]}
    state.write_text(json.dumps(result,indent=2)+'\n')
    code=code or shutil.which('code') or '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code'
    if not Path(code).exists():raise ValueError('VS Code CLI is unavailable; rerun after installing VS Code.')
    installed=runner([code,'--list-extensions'],text=True,capture_output=True,check=True).stdout.lower().splitlines()
    for extension in (PROFILE/'extensions.txt').read_text().splitlines():
        if not extension or extension.startswith('#') or extension.lower() in installed:continue
        print(f'Install VS Code extension {extension}')
        response=runner([code,'--install-extension',extension],text=True,capture_output=True)
        if response.returncode:
            result['failed_extensions'].append(extension)
            print(f'Could not install {extension}; see the final report.')
        state.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    try:seed(Path.home(),args.apply)
    except (OSError,ValueError,subprocess.CalledProcessError) as error:
        print(f'Error: {error}',file=sys.stderr);sys.exit(1)
