#!/usr/bin/env sh
# Build the installable theme zip: tod-pink.zip in the repo root.
# WordPress accepts it directly: Design → Themes → Hinzufügen → Theme hochladen.
set -e
cd "$(dirname "$0")/.."
git archive --format=zip --prefix=tod-pink/ -o tod-pink.zip HEAD
echo "tod-pink.zip ready."
