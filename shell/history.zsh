# Directory-specific command history. Leading-space commands remain private.
LC_DELIMITER_START='⋮'
LC_DELIMITER_END='⭐'
function zshaddhistory() {
  [[ "$1" == $'\n' || "$1" == ' '* ]] && return
  local ignored
  for ignored in ls ll cd j git gss gap lc ggpush ggpull; do
    [[ "$1" == "$ignored "* || "$1" == "$ignored"$'\n' ]] && return
  done
  print -r -- "${1%%$'\n'}${LC_DELIMITER_START}${PWD}${LC_DELIMITER_END}" >> "$HOME/.lc_history"
}
function lc() {
  [[ -f "$HOME/.lc_history" ]] || return 0
  local selected
  selected=$(python3 - "$PWD" "$HOME/.lc_history" <<'PY'
import sys
for line in reversed(open(sys.argv[2]).read().splitlines()):
    if line.endswith('⋮'+sys.argv[1]+'⭐'):
        print(line.rsplit('⋮',1)[0])
PY
  )
  selected=$(print -r -- "$selected" | fzf) || return 0
  [[ -n "$selected" ]] && print -z -- "$selected"
}
