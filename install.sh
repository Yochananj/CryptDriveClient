#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Yochananj/CryptDriveClient.git"
INSTALL_DIR="$HOME/.cryptdrive/client"
VENV_PYTHON="$INSTALL_DIR/.venv/bin/python"
CONSTANTS_FILE="$INSTALL_DIR/src/Dependencies/Constants.py"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

echo -e "${BOLD}${CYAN}"
echo "  ╔════════════════════════════════╗"
echo "  ║   CryptDrive Client Installer  ║"
echo "  ╚════════════════════════════════╝"
echo -e "${NC}"

# ── Dependency checks ────────────────────────────────────────────────────────
for cmd in git python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo -e "${RED}Error: '$cmd' is required but not installed.${NC}"
        exit 1
    fi
done

# ── Clone / update repo ──────────────────────────────────────────────────────
echo -e "${CYAN}Fetching CryptDrive client...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    git -C "$INSTALL_DIR" pull --quiet
else
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --quiet "$REPO_URL" "$INSTALL_DIR"
fi

# ── Prompt for server IP ─────────────────────────────────────────────────────
echo ""
while true; do
    read -rp "Enter the CryptDrive server IP address: " SERVER_IP
    if [[ -z "$SERVER_IP" ]]; then
        echo -e "${RED}IP address cannot be empty. Please try again.${NC}"
    elif [[ ! "$SERVER_IP" =~ ^[a-zA-Z0-9._-]+$ ]]; then
        echo -e "${RED}Invalid format. Please enter a valid IP or hostname.${NC}"
    else
        break
    fi
done

# ── Write server address into constants file ──────────────────────────────────
echo -e "${CYAN}Configuring server address...${NC}"
if [ ! -f "$CONSTANTS_FILE" ]; then
    echo -e "${RED}Error: constants file not found at $CONSTANTS_FILE${NC}"
    exit 1
fi

sed -i.bak "s|^server_address = \".*\"|server_address = \"$SERVER_IP\"|" "$CONSTANTS_FILE"
rm -f "$CONSTANTS_FILE.bak"

echo -e "${GREEN}  Server address set to: $SERVER_IP${NC}"

# ── Create virtual environment ───────────────────────────────────────────────
echo -e "${CYAN}Setting up Python environment...${NC}"
if [ ! -d "$INSTALL_DIR/.venv" ]; then
    python3 -m venv "$INSTALL_DIR/.venv"
fi

# ── Install dependencies ─────────────────────────────────────────────────────
echo -e "${CYAN}Installing dependencies...${NC}"
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -e "$INSTALL_DIR"

# ── Create native launcher ───────────────────────────────────────────────────
if [[ "$(uname)" == "Darwin" ]]; then
    APP_BUNDLE="/Applications/CryptDrive.app"
    mkdir -p "$APP_BUNDLE/Contents/MacOS"

    cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
    <key>CFBundleExecutable</key>  <string>CryptDrive</string>
    <key>CFBundleIdentifier</key> <string>com.cryptdrive.app</string>
    <key>CFBundleName</key>       <string>CryptDrive</string>
    <key>CFBundleVersion</key>    <string>1.0.0</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>LSUIElement</key>        <false/>
</dict></plist>
EOF

    cat > "$APP_BUNDLE/Contents/MacOS/CryptDrive" << EOF
#!/usr/bin/env bash
exec "$VENV_PYTHON" "$INSTALL_DIR/src/main.py" "\$@"
EOF
    chmod +x "$APP_BUNDLE/Contents/MacOS/CryptDrive"
    echo -e "\n${GREEN}✓ Installed to /Applications/CryptDrive.app${NC}"

else
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/cryptdrive.desktop" << EOF
[Desktop Entry]
Name=CryptDrive
Comment=Zero-knowledge encrypted cloud storage
Exec=$VENV_PYTHON $INSTALL_DIR/src/main.py
Icon=$INSTALL_DIR/assets/icon.png
Type=Application
Terminal=false
Categories=Utility;Network;
EOF

    mkdir -p "$HOME/.local/bin"
    cat > "$HOME/.local/bin/cryptdrive" << EOF
#!/usr/bin/env bash
exec "$VENV_PYTHON" "$INSTALL_DIR/src/main.py" "\$@"
EOF
    chmod +x "$HOME/.local/bin/cryptdrive"

    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [ -f "$rc" ] && ! grep -q '\.local/bin' "$rc"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
        fi
    done

    echo -e "\n${GREEN}✓ CryptDrive added to your app menu.${NC}"
    echo -e "${GREEN}  You can also launch it by running: cryptdrive${NC}"
fi
