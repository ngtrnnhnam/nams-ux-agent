#!/bin/sh
# Rasterise footer-kv-*.svg to @2x PNG with headless Chrome.
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in footer-kv-*.svg; do
  n="${f%.svg}"
  printf '<html><body style="margin:0"><img src="%s" width="1440" height="480"></body></html>' "$f" > ".render-$n.html"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size=1440,480 --screenshot="$PWD/$n@2x.png" "file://$PWD/.render-$n.html" >/dev/null 2>&1
  rm -f ".render-$n.html"
done
ls -1 footer-kv-*@2x.png
