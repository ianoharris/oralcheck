#!/usr/bin/env bash
# Installs OralCheck Studio on the PC hub (ianspc). Safe to run again.
#   ssh ianoharris@ianspc 'bash -s' < oralcheck-agent/studio/install.sh
# It clones the repo to ~/oralcheck-studio/repo, makes a venv, runs the app as a
# user service on 127.0.0.1:8797, and serves it on the tailnet only at
# https://ianspc.tailed990a.ts.net:8797 (never Funnel: nothing public).
set -euo pipefail
HOME_DIR="$HOME/oralcheck-studio"
PORT=8797
mkdir -p "$HOME_DIR"/{data,photos,keys}
chmod 700 "$HOME_DIR/keys"

if [ ! -d "$HOME_DIR/repo/.git" ]; then
  gh repo clone ianoharris/oralcheck "$HOME_DIR/repo" -- -q
fi
git -C "$HOME_DIR/repo" config user.name "OralCheck Studio"
git -C "$HOME_DIR/repo" config user.email "bot@oralcheck.org"
gh auth setup-git >/dev/null 2>&1 || true
git -C "$HOME_DIR/repo" pull -q --rebase origin master

if [ ! -x "$HOME_DIR/venv/bin/python" ]; then
  python3 -m venv "$HOME_DIR/venv"
fi
"$HOME_DIR/venv/bin/pip" install -q --upgrade pip
"$HOME_DIR/venv/bin/pip" install -q "fastapi>=0.115" "uvicorn>=0.30" "python-multipart>=0.0.9"

mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/oralcheck-studio.service" <<UNIT
[Unit]
Description=OralCheck Studio -- posting calendar app (loopback :$PORT, tailnet via tailscale serve)
After=network-online.target

[Service]
WorkingDirectory=$HOME_DIR/repo/oralcheck-agent/studio
Environment=STUDIO_HOME=$HOME_DIR
Environment=STUDIO_PORT=$PORT
Environment=PATH=$HOME/.local/bin:/snap/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$HOME_DIR/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now oralcheck-studio.service
systemctl --user restart oralcheck-studio.service

if ! tailscale serve status 2>/dev/null | grep -q ":$PORT "; then
  tailscale serve --bg --https=$PORT "http://127.0.0.1:$PORT" || \
    echo "NOTE: tailscale serve needs operator rights; run: sudo tailscale serve --bg --https=$PORT http://127.0.0.1:$PORT"
fi
echo "OralCheck Studio: https://ianspc.tailed990a.ts.net:$PORT"
