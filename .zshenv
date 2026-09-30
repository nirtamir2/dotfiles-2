# Optional runtime installers own these files. Never fail when they are absent.
for runtime_env in "$HOME/.cargo/env" "$HOME/.rover/env" "$HOME/.vite-plus/env"; do
  [[ -f "$runtime_env" ]] && source "$runtime_env"
done
unset runtime_env
