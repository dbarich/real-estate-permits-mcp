#!/usr/bin/env bash
# =============================================================================
# Real Estate Permits MCP — Quick Start Setup
# =============================================================================
# This script:
#   1. Checks for Python 3 and pip
#   2. Installs dependencies (mcp, httpx)
#   3. Runs a smoke test to verify the server can reach live APIs
#   4. Generates the Claude Desktop config snippet
#   5. Offers to inject it into your claude_desktop_config.json
#
# Usage:
#   git clone https://github.com/dbarich/real-estate-permits-mcp.git
#   cd real-estate-permits-mcp
#   chmod +x setup.sh && ./setup.sh
# =============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_PATH="$REPO_DIR/src/seattle_permits_server.py"

# Colors (safe fallback if terminal doesn't support them)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[info]${NC}  $1"; }
ok()    { echo -e "${GREEN}[ok]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $1"; }
fail()  { echo -e "${RED}[fail]${NC}  $1"; }

echo ""
echo "=========================================="
echo "  Real Estate Permits MCP — Quick Start"
echo "=========================================="
echo ""

# ---- Step 1: Check Python 3 ----
info "Checking for Python 3..."

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PY_VERSION=$(python --version 2>&1)
    if [[ "$PY_VERSION" == *"3."* ]]; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    fail "Python 3 not found. Install it from https://python.org or via 'brew install python'"
    exit 1
fi

PY_VERSION=$($PYTHON_CMD --version 2>&1)
ok "Found $PY_VERSION ($PYTHON_CMD)"

# ---- Step 2: Install dependencies ----
info "Installing dependencies (mcp, httpx)..."

if $PYTHON_CMD -m pip install mcp httpx --quiet 2>/dev/null; then
    ok "Dependencies installed"
else
    warn "pip install failed with default flags, trying --break-system-packages..."
    $PYTHON_CMD -m pip install mcp httpx --break-system-packages --quiet
    ok "Dependencies installed (with --break-system-packages)"
fi

# ---- Step 3: Smoke test ----
info "Running smoke test against live APIs..."
echo ""

SMOKE_RESULT=$($PYTHON_CMD -c "
import asyncio, sys
sys.path.insert(0, '$REPO_DIR/src')
import seattle_permits_server as s

async def smoke():
    # Test 1: Socrata (Seattle permits)
    try:
        result = await s.search_permits('DEARBORN', days_back=90)
        if result.startswith('Error') or 'timed out' in result.lower():
            print('SOCRATA_FAIL: ' + result[:100])
            return False
        lines = result.strip().split(chr(10))
        print('SOCRATA_OK: ' + lines[0])
    except Exception as e:
        print('SOCRATA_FAIL: ' + str(e)[:100])
        return False

    # Test 2: King County GIS (parcel lookup)
    try:
        result = await s.get_parcel_by_pin('6362900036')
        if result.startswith('Error') or 'timed out' in result.lower():
            print('KC_GIS_FAIL: ' + result[:100])
            return False
        print('KC_GIS_OK: Parcel lookup returned ' + str(len(result)) + ' chars')
    except Exception as e:
        print('KC_GIS_FAIL: ' + str(e)[:100])
        return False

    return True

ok = asyncio.run(smoke())
sys.exit(0 if ok else 1)
" 2>/dev/null)

SMOKE_EXIT=$?

echo "$SMOKE_RESULT" | while IFS= read -r line; do
    if [[ "$line" == *"_OK:"* ]]; then
        ok "$line"
    else
        fail "$line"
    fi
done

if [ $SMOKE_EXIT -ne 0 ]; then
    fail "Smoke test failed. Check your internet connection and try again."
    echo "  The tool queries free public APIs (data.seattle.gov, gismaps.kingcounty.gov)."
    echo "  If you're behind a VPN or firewall, you may need to allowlist these domains."
    exit 1
fi

echo ""
ok "Smoke test passed — both APIs responding"

# ---- Step 4: Generate Claude Desktop config ----
echo ""
info "Generating Claude Desktop configuration..."

CONFIG_SNIPPET=$(cat <<EOF
{
  "mcpServers": {
    "real-estate-permits": {
      "command": "$PYTHON_CMD",
      "args": ["$SERVER_PATH"]
    }
  }
}
EOF
)

echo ""
echo "Add this to your claude_desktop_config.json:"
echo ""
echo "$CONFIG_SNIPPET"
echo ""

# ---- Step 5: Offer to auto-configure ----
# Detect config file location
CONFIG_PATH=""
if [ "$(uname)" = "Darwin" ]; then
    CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [ "$(uname)" = "Linux" ]; then
    CONFIG_PATH="$HOME/.config/Claude/claude_desktop_config.json"
fi

if [ -n "$CONFIG_PATH" ]; then
    if [ -f "$CONFIG_PATH" ]; then
        # Check if already configured
        if grep -q "real-estate-permits" "$CONFIG_PATH" 2>/dev/null; then
            ok "Claude Desktop already configured (found 'real-estate-permits' in config)"
        else
            echo ""
            read -p "$(echo -e ${YELLOW}Would you like me to add this to your Claude Desktop config? [y/N]${NC} )" -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                # Back up existing config
                cp "$CONFIG_PATH" "$CONFIG_PATH.backup.$(date +%Y%m%d%H%M%S)"
                ok "Backed up existing config"

                # Merge using Python (handles existing mcpServers key)
                $PYTHON_CMD -c "
import json, sys

config_path = '''$CONFIG_PATH'''
server_path = '''$SERVER_PATH'''
python_cmd = '''$PYTHON_CMD'''

with open(config_path) as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['real-estate-permits'] = {
    'command': python_cmd,
    'args': [server_path]
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('OK')
"
                ok "Config updated. Restart Claude Desktop to activate."
            else
                info "No changes made. Add the config manually when ready."
            fi
        fi
    else
        warn "Claude Desktop config not found at expected path."
        info "Create the file at: $CONFIG_PATH"
        info "Or paste the JSON snippet above into your existing config."
    fi
fi

# ---- Done ----
echo ""
echo "=========================================="
echo "  Setup Complete"
echo "=========================================="
echo ""
echo "  Next steps:"
echo "  1. Restart Claude Desktop"
echo "  2. Look for 'real-estate-permits' in the tools menu"
echo "  3. Try asking Claude:"
echo ""
echo "     \"Search for building permits on Dearborn Street\""
echo "     \"Look up parcel 6362900036\""
echo "     \"Find multifamily permits issued in the last year\""
echo ""
echo "  For the full getting-started guide, see:"
echo "  $REPO_DIR/QUICKSTART.md"
echo ""
