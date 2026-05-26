#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.cryptdrive/client"
APP_BUNDLE="/Applications/CryptDrive.app"
DESKTOP_ENTRY="$HOME/.local/share/applications/cryptdrive.desktop"
CLI_BIN="$HOME/.local/bin/cryptdrive"
LOG_FILE_MAC="$HOME/Library/Logs/CryptDrive.log"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

echo -e "${BOLD}${RED}"
echo "  ╔═════════════════════════════════╗"
echo "  ║  CryptDrive Client Uninstaller  ║"
echo "  ╚═════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}The following items will be removed:${NC}"

# Check for universal files
[ -d "$INSTALL_DIR" ]   && echo " - Core files & environment: $INSTALL_DIR"

# Check for macOS specific files
if [[ "$(uname)" == "Darwin" ]]; then
   [ -d "$APP_BUNDLE" ]    && echo " - macOS Application:      $APP_BUNDLE"
   [ -f "$LOG_FILE_MAC" ]  && echo " - Log files:             $LOG_FILE_MAC"
fi

# Check for Linux specific files
if [[ "$(uname)" == "Linux" ]]; then
   [ -f "$DESKTOP_ENTRY" ] && echo " - Desktop entry:         $DESKTOP_ENTRY"
   [ -f "$CLI_BIN" ]       && echo " - CLI Command:           $CLI_BIN"
fi

echo ""
read -rp "Are you sure you want to uninstall CryptDrive? (y/N): " CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
   echo -e "${CYAN}Uninstallation cancelled.${NC}"
   exit 0
fi

echo -e "${CYAN}Uninstalling...${NC}"

# Remove core files
rm -rf "$INSTALL_DIR"

# OS Specific cleanup
if [[ "$(uname)" == "Darwin" ]]; then
   rm -rf "$APP_BUNDLE"
   rm -f "$LOG_FILE_MAC"
elif [[ "$(uname)" == "Linux" ]]; then
   rm -f "$DESKTOP_ENTRY"
   rm -f "$CLI_BIN"
   # Note: We don't automatically strip the PATH export from .bashrc/.zshrc
   # to avoid accidental corruption, but the binary itself is gone.
fi

echo -e "${GREEN}✓ CryptDrive has been successfully uninstalled.${NC}"