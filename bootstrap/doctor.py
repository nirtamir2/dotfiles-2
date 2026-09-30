#!/usr/bin/env python3
"""Read-only restore audit. --report saves a local checklist without exposing secrets."""
import argparse
import json
import os
from pathlib import Path
import shutil
from manage import ROOT, check_parents, manifest, same_link


def audit(home):
    lines=['# New Mac: remaining steps','', 'Automatic installation cannot restore account logins, keychain entries or macOS privacy permissions.','']
    missing=[dst for src,dst in manifest('core',home) if not same_link(home/dst,ROOT/src)]
    lines+=['## Dotfiles', '']
    lines += ['- Core files not linked to this checkout: '+', '.join('`~/'+x+'`' for x in missing)] if missing else ['- All core links point to this checkout.']
    old=[]
    for parent in [home,home/'.oh-my-zsh/custom',home/'.config',home/'.local/bin']:
        if not parent.is_dir():continue
        for p in parent.iterdir():
            if p.is_symlink():
                destination=p.resolve()
                if destination.is_relative_to(home/'dotfiles') and not destination.is_relative_to(ROOT):old.append('~/'+str(p.relative_to(home)))
    if old:lines.append('- Still depend on the old ~/dotfiles folder: '+', '.join('`'+x+'`' for x in sorted(old))+'. Keep it until these are migrated.')
    missing_commands=[x for x in ['brew','git','gpg','fnm','zoxide','fzf','starship','mcfly','bat','eza'] if not shutil.which(x)]
    lines.append('- Missing commands on this process PATH: '+(', '.join(missing_commands) if missing_commands else 'none of the core runtime commands checked')+'.')
    for name in ['vscode','desktop']:
        p=home/'.local/state/dotfiles'/(name+'.json')
        if p.is_file():
            data=json.loads(p.read_text())
            if data.get('failed_extensions'):lines.append('- VS Code extensions needing retry: '+', '.join(data['failed_extensions'])+'. Rerun ./setup install to retry missing extensions.')
            if data.get('skipped_domains'):lines.append('- App preferences skipped because apps were running: '+', '.join(data['skipped_domains'])+'. Quit those apps and run ./setup desktop --apply.')
    lines+=['','## App settings and permissions','',
      '- Raycast: import a fresh settings export or sign in to Cloud Sync. The hotkey inventory is documentation, not an importable backup. Confirm Right Option Hyper (Include Shift) and Option-Space.',
      '- Raycast: register this checkout’s raycast/scripts/quick open and raycast/scripts/custom folders. Custom extension accounts/preferences stay in Raycast.',
      '- Grant Accessibility to Raycast and Homerow; Screen Recording to Zappy/QuickTime; microphone permission where needed. macOS requires these on the new machine.',
      '- Homerow: verify Hyper+H hints and Hyper+J scrolling. Enable launch at login through the app if macOS requires confirmation.',
      '- Warp: existing settings are preserved; fresh installs receive reviewed appearance/input/privacy preferences and the Classic Vivid theme. Sign in separately. Agent permissions/MCP and account/session data are not copied.',
      '- VS Code: a fresh default profile uses your current Cursor Default snapshot. Existing editor files are never overwritten by install. Home/Work profile exports remain available for optional import.',
      '- Restart apps or log out to load restored macOS preferences. Confirm native screenshot shortcuts and /tmp destination.',
      '- Dictation: use built-in macOS Dictation. In System Settings → Keyboard → Dictation, confirm On, US English + Hebrew, Press Right Command Key Twice, and Automatic microphone. Allow macOS to download speech assets; see manual-install/dictation.md.',
      '- Native screen zoom: test Right Ctrl + mouse wheel. In System Settings → Accessibility → Zoom, confirm scroll gesture enabled, modifier Control and Zoom style Full Screen. The gesture/modifier keys are restored by ./setup install or ./setup defaults; macos-defaults/zoom.yaml supports the direct macos-defaults tool.',
      '- Optional Schnitz Neovim downloads plugins on first launch. With --with-tmux, use Ctrl-S then Shift-I inside tmux to install plugins.',
      '', '## Private transfers and accounts','',
      '- GPG: securely transfer/import your existing signing key and owner trust, or configure a new key. Signing is enabled in Git; commits may fail until the matching secret key is present.',
      '- SSH: restore reviewed ~/.ssh/config, its includes and agent/key setup securely. Do not copy known_hosts blindly or put private keys in this repo.',
      '- npm: restore registry authentication locally. The repository’s sanitized .npmrc contains no credentials and is not installed by this command.',
      '- Run gh auth login, and sign in to browsers, app stores, chat/work apps, password manager, and any cloud/development services you use.',
      '- Transfer project directories, Obsidian vaults, databases and Syncthing configuration/data separately. They are not dotfiles.',
      '- Optional continuity: transfer zoxide history, shell history and local snippets privately. Histories may contain secrets; they are deliberately excluded from Git.',
      '- Review agent-tool settings/MCP servers/skills (for example ~/.agents, ~/.codex, ~/.claude, ~/.config/opencode) before private transfer; they may contain credentials or machine-specific paths.',
      '- Review local services: Borders, Syncthing, Watchman and any project services. The installer does not blindly start copied LaunchAgents.',
      '', '## Scope','',
      '- Default install includes the existing extras manifest. Entries already marked unavailable/disabled remain manual-review items in packages/availability-review.json.',
      '- Historical npm globals require --with-node-globals; work apps require --with-work; App Store apps require --with-mas and an authenticated App Store session.',
      '- No commits or pushes are performed. New/untracked work must be transferred with the checkout; a fresh clone will not contain uncommitted changes or the ignored .private archive.',
      '- See docs/NEW-MAC.md and docs/MACHINE-AUDIT.md for full scope and source evidence.', '']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',action='store_true');args=parser.parse_args()
    home=Path.home();text=audit(home)
    print(text)
    if args.report:
        path=home/'.local/state/dotfiles/next-steps.md';check_parents(path,home);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with path.open('w') as file:os.chmod(path,0o600);file.write(text)
        print('Saved:',path)

if __name__=='__main__':main()
