"""
First Chord Brain — Workspace Path Configuration
=================================================
Single source of truth for all cross-tool file paths.

All paths are derived relative to this file's location so the entire
FirstChord/ workspace can be moved without touching any other file.

Structure assumed:
    FirstChord/
    ├── first-chord-brain/   ← this file lives here
    ├── music-school-dashboard/
    └── payment-pause-pwa/
"""

from pathlib import Path

# ── Workspace root (FirstChord/) ───────────────────────────────────────────────
WORKSPACE = Path(__file__).parent.parent

# ── Tool roots ────────────────────────────────────────────────────────────────
BRAIN_DIR         = Path(__file__).parent
DASHBOARD_DIR     = WORKSPACE / "music-school-dashboard"
PAYMENT_PAUSE_DIR = WORKSPACE / "payment-pause-pwa"

# ── Key files and directories ─────────────────────────────────────────────────
REGISTRY_PATH  = DASHBOARD_DIR / "lib" / "config" / "students-registry.js"
FC_EXPORTS_DIR = BRAIN_DIR / "exports" / "fc_identity_layer"
VAULT_DIR      = BRAIN_DIR / "vault"

# ── Credentials (stay in home dir — not tool-specific) ────────────────────────
TOKEN_FILE   = Path.home() / "token_musiclessons.json"
CREDS_FILE   = Path.home() / "credentials_musiclessons.json"
