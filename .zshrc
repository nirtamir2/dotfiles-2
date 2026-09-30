# Nir's interactive shell. Dependencies are installed explicitly with ./setup shell.
export DOTFILES_ROOT="${DOTFILES_ROOT:-${${(%):-%N}:A:h}}"
export ZSH="$HOME/.oh-my-zsh"
export GOPATH="$HOME/.go-modules"
export PNPM_HOME="$HOME/Library/pnpm"
export EDITOR='code --wait'
export VISUAL='code --wait'
export LC_ALL=en_US.UTF-8
export ZSH_PLUGINS_ALIAS_TIPS_TEXT='❗  Use the alias: '
export BAT_THEME=base16

typeset -U path PATH
path=("$DOTFILES_ROOT/bin" "$PNPM_HOME/bin" "$PNPM_HOME" "$HOME/.local/bin" "$HOME/bin" "$HOME/.bin" "$GOPATH/bin" "$HOME/.cargo/bin" "$HOME/.bun/bin" "$HOME/.console-ninja/.bin" "$HOME/.opencode/bin" "$HOME/.antigravity/antigravity/bin" /opt/homebrew/bin /opt/homebrew/sbin /usr/local/bin /usr/local/sbin $path)
for prefix in /opt/homebrew /usr/local; do
  for tool in libpq openjdk curl; do
    [[ -d "$prefix/opt/$tool/bin" ]] && path+=("$prefix/opt/$tool/bin")
  done
 done
[[ -d /Applications/WebStorm.app/Contents/MacOS ]] && path+=(/Applications/WebStorm.app/Contents/MacOS)

unsetopt RM_STAR_SILENT
setopt RM_STAR_WAIT HIST_IGNORE_SPACE HIST_IGNORE_ALL_DUPS INC_APPEND_HISTORY
HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
HIST_STAMPS=dd-mm-yyyy
fpath=("$DOTFILES_ROOT/shell/completions" $fpath)
ZSH_THEME=''
plugins=(git last-working-dir)
if [[ -f "$ZSH/oh-my-zsh.sh" ]]; then
  # Use an isolated custom directory so the old repo's aliases are not loaded twice.
  ZSH_CUSTOM="$DOTFILES_ROOT/shell/omz"
  source "$ZSH/oh-my-zsh.sh"
else
  autoload -Uz compinit; compinit
fi
# Plugin sources live outside the repository; load existing optional plugins explicitly.
for plugin in zsh-autosuggestions zsh-npm-scripts-autocomplete alias-tips fast-syntax-highlighting; do
  [[ -f "$ZSH/custom/plugins/$plugin/$plugin.plugin.zsh" ]] && source "$ZSH/custom/plugins/$plugin/$plugin.plugin.zsh"
done
source "$DOTFILES_ROOT/shell/aliases.zsh"
source "$DOTFILES_ROOT/shell/functions.zsh"
source "$DOTFILES_ROOT/shell/history.zsh"

(( $+commands[fnm] )) && eval "$(fnm env --use-on-cd --shell zsh)"
source "$DOTFILES_ROOT/shell/navigation.zsh"
if (( $+commands[fzf] )); then
  # Keep McFly's Ctrl-R; fzf still supplies Ctrl-T and Alt-C.
  FZF_CTRL_R_COMMAND='' source <(fzf --zsh)
fi
(( $+commands[mcfly] )) && eval "$(mcfly init zsh)"
export STARSHIP_CONFIG="${STARSHIP_CONFIG:-$HOME/.starship.toml}"
(( $+commands[starship] )) && eval "$(starship init zsh)"
(( $+commands[wt] )) && eval "$(command wt config shell init zsh)"
if [[ -f "$HOME/.local/share/dotfiles/pnpm-completion.zsh" ]]; then
  source "$HOME/.local/share/dotfiles/pnpm-completion.zsh"
elif [[ -f "$HOME/completion-for-pnpm.zsh" ]]; then
  source "$HOME/completion-for-pnpm.zsh"
fi
[[ -f "$HOME/.vite-plus/env" ]] && source "$HOME/.vite-plus/env"
[[ -n "$GHOSTTY_RESOURCES_DIR" && -f "$GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration" ]] && source "$GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration"
[[ -f "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"
# No npm subprocess at shell startup. Enable NODE_PATH in .zshrc.local if needed.
bindkey '^A' beginning-of-line
bindkey '^E' end-of-line
bindkey '^L' clear-screen
autoload -Uz edit-command-line
zle -N edit-command-line
bindkey '^X^E' edit-command-line
true
