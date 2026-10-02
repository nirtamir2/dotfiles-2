# Claude

The Claude desktop app is managed by `cask "claude"` in the extras Brewfile.

Claude Code uses the [official native installer](https://code.claude.com/docs/en/setup)
on the latest release channel, with background auto-updates. It installs at
`~/.local/bin/claude`; `.zshrc` already includes that directory in `PATH`.
The default `./setup install` includes it with extras; `--minimal` skips it.

Install separately:

```sh
./setup claude
claude --version
claude doctor
```

To migrate an existing Homebrew installation, close Claude Code sessions first:

```sh
brew uninstall --cask claude-code # use claude-code@latest if that was your cask
./setup claude
rehash
claude --version
```

Uninstall without `--zap` to preserve settings and history. `./setup claude`
retains an existing native installation; run `claude update` for an immediate
update. The native launcher must remain first on `PATH` if you have other installs.
