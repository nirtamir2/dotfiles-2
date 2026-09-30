#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Open dotfiles
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🤖

# Documentation:
# @raycast.description Open dotfiles in VS Code
# @raycast.author Nir Tamir
# @raycast.authorURL https://nirtamir.com

ROOT="$(cd -- "$(dirname -- "$0")/../../.." && pwd)"
code "$ROOT"

