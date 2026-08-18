#!/usr/bin/env sh
# Build the installable theme zip: tod-pink.zip in the repo root.
# WordPress accepts it directly: Design → Themes → Hinzufügen → Theme hochladen.
#
# Licensed fonts dropped into assets/fonts/ (e.g. EMOTIQ.woff2) are kept
# out of git but ARE packed into the zip, so the installed theme carries them.
set -e
cd "$(dirname "$0")/.."
if [ -n "$(git status --porcelain)" ]; then
	echo "WARNING: working tree has uncommitted changes - the zip is built from HEAD and will NOT contain them." >&2
fi
git archive --format=zip --prefix=tod-pink/ -o tod-pink.zip HEAD
python3 - <<'EOF'
import glob, os, zipfile
fonts = [f for f in glob.glob('assets/fonts/*') if not f.endswith('README.txt')]
if fonts:
    with zipfile.ZipFile('tod-pink.zip', 'a', zipfile.ZIP_DEFLATED) as z:
        for f in fonts:
            z.write(f, 'tod-pink/' + f)
            print('packed licensed font:', f)
EOF
echo "tod-pink.zip ready."
