#!/usr/bin/env sh
# Point Labs at a different domain.
#
#   ./set-domain.sh labs-rouge.vercel.app
#   ./set-domain.sh labs.example.com
#
# The domain lives in one place, SITE['domain'] in tools/data.py. This rewrites
# it there and regenerates the pages, vercel.json, sitemap.xml and robots.txt,
# so canonical URLs and the Open Graph / Twitter tags all follow. Safe to rerun.

set -e

NEW="$1"
if [ -z "$NEW" ]; then
  echo "usage: ./set-domain.sh <domain>   (no https://, no trailing slash)" >&2
  exit 1
fi
NEW=$(printf '%s' "$NEW" | sed -e 's#^https\{0,1\}://##' -e 's#/$##')

cd "$(dirname "$0")"
python3 - "$NEW" <<'PY'
import re, sys
path = 'tools/data.py'
text = open(path, encoding='utf-8').read()
updated, count = re.subn(r"domain='https://[^']*'", "domain='https://%s'" % sys.argv[1], text)
if count != 1:
    sys.exit('could not find the domain in tools/data.py')
open(path, 'w', encoding='utf-8').write(updated)
PY
python3 tools/build.py
echo "Domain set to https://$NEW"
