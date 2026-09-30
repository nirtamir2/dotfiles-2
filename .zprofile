# Login-shell paths. Safe on a new Mac before optional runtimes exist.
for brew_bin in /opt/homebrew/bin/brew /usr/local/bin/brew; do
  if [[ -x "$brew_bin" ]]; then
    eval "$("$brew_bin" shellenv)"
    break
  fi
done
export PYENV_ROOT="$HOME/.pyenv"
[[ -d "$PYENV_ROOT/bin" ]] && path=("$PYENV_ROOT/bin" $path)
(( $+commands[pyenv] )) && eval "$(pyenv init --path)"
path=("$HOME/.local/bin" $path)
typeset -U path PATH
