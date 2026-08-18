#!/usr/bin/env sh
# Build the Divi child theme zip: tod-pink-divi-child.zip in the repo root.
# Assembles divi/child/ plus the shared assets (fonts.css, tod.css, tod.js)
# from the block theme - single source of truth, copied at build time.
# Licensed fonts dropped into assets/fonts/ are packed in as well.
set -e
cd "$(dirname "$0")/.."
if [ -n "$(git status --porcelain)" ]; then
	echo "WARNING: working tree has uncommitted changes - shared assets are copied from the working tree as-is." >&2
fi
python3 - <<'EOF'
import glob, os, shutil, tempfile, zipfile

root = os.getcwd()
tmp = tempfile.mkdtemp()
child = os.path.join(tmp, 'tod-pink-divi-child')

shutil.copytree('divi/child', child)
os.makedirs(os.path.join(child, 'assets/js'), exist_ok=True)
shutil.copy('assets/css/fonts.css', os.path.join(child, 'assets/css/fonts.css'))
shutil.copy('assets/css/tod.css', os.path.join(child, 'assets/css/tod.css'))
shutil.copy('assets/js/tod.js', os.path.join(child, 'assets/js/tod.js'))
shutil.copy('screenshot.png', os.path.join(child, 'screenshot.png'))

fonts = [f for f in glob.glob('assets/fonts/*') if not f.endswith('README.txt')]
if fonts:
    os.makedirs(os.path.join(child, 'assets/fonts'), exist_ok=True)
    for f in fonts:
        shutil.copy(f, os.path.join(child, 'assets/fonts', os.path.basename(f)))
        print('packed licensed font:', f)

out = os.path.join(root, 'tod-pink-divi-child.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for base, _, files in os.walk(tmp):
        for name in files:
            full = os.path.join(base, name)
            z.write(full, os.path.relpath(full, tmp))
shutil.rmtree(tmp)
print('tod-pink-divi-child.zip ready.')
EOF
