# One directory database; keep Nir's familiar j and offer zi/ji for fuzzy selection.
if (( $+commands[zoxide] )); then
  eval "$(zoxide init zsh)"
  alias j='z'
  alias ji='zi'
fi
