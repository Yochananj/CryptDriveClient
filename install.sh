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

# ── Pick the right Python on Apple Silicon ────────────────────────────────────
# Check the Python binary's actual architecture, not the shell's — the shell
# may be running under Rosetta even on Apple Silicon hardware.
PYTHON3="$(command -v python3)"
PYTHON3_ARCH="$(file "$PYTHON3" 2>/dev/null || true)"

if [[ "$(sysctl -n hw.optional.arm64 2>/dev/null)" == "1" ]]; then
    # This Mac has Apple Silicon hardware
    if [[ -x "/opt/homebrew/bin/python3" ]]; then
        PYTHON3="/opt/homebrew/bin/python3"
        echo -e "${CYAN}Apple Silicon detected — using native arm64 Python at /opt/homebrew/bin/python3.${NC}"
    else
        echo -e "${RED}Error: Apple Silicon detected but native Homebrew Python not found.${NC}"
        echo -e "${RED}Install it with: brew install python3${NC}"
        exit 1
    fi
fi

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
# Always recreate the venv to ensure it matches the correct architecture
rm -rf "$INSTALL_DIR/.venv"
"$PYTHON3" -m venv "$INSTALL_DIR/.venv"

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
    <key>CFBundleExecutable</key>        <string>CryptDrive</string>
    <key>CFBundleIdentifier</key>        <string>com.cryptdrive.app</string>
    <key>CFBundleName</key>              <string>CryptDrive</string>
    <key>CFBundleVersion</key>           <string>1.0.0</string>
    <key>CFBundlePackageType</key>       <string>APPL</string>
    <key>LSUIElement</key>               <false/>
    <key>LSRequiresNativeExecution</key> <true/>
</dict></plist>
EOF

    cat > "$APP_BUNDLE/Contents/MacOS/CryptDrive" << EOF
#!/usr/bin/env bash

# Force native arm64 — prevents Rosetta from launching this as x86_64
if [[ "\$(uname -m)" != "arm64" ]]; then
    exec arch -arm64 /bin/bash "\$0" "\$@"
fi

# Set working directory so relative imports work
cd "$INSTALL_DIR" || exit 1

# Log crashes to ~/Library/Logs/CryptDrive.log
mkdir -p "\$HOME/Library/Logs"
exec "$VENV_PYTHON" "$INSTALL_DIR/src/main.py" "\$@" \
    >> "\$HOME/Library/Logs/CryptDrive.log" 2>&1
EOF
    chmod +x "$APP_BUNDLE/Contents/MacOS/CryptDrive"

    # Clear Gatekeeper quarantine so macOS doesn't block the unsigned app
    xattr -cr "$APP_BUNDLE" 2>/dev/null || true

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