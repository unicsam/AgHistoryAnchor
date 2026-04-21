import os

# ==============================================================================
# CONFIGURATION & PATHS
# ==============================================================================

# Global IDE Paths
GLOBAL_BASE = os.path.join(os.environ['APPDATA'], 'antigravity')
GLOBAL_DB = os.path.join(GLOBAL_BASE, 'User', 'globalStorage', 'state.vscdb')

# Data Directories
CONVERSATIONS_DIR = os.path.join(os.path.expanduser('~'), '.gemini', 'antigravity', 'conversations')
BRAIN_DIR = os.path.join(os.path.expanduser('~'), '.gemini', 'antigravity', 'brain')

# SQLite Keys
PB_KEY = "antigravityUnifiedStateSync.trajectorySummaries"
JSON_KEY = "chat.ChatSessionStore.index"

# Backup Settings
BACKUP_PREFIX = "ag_backup"
BACKUP_DIR_NAME = ".antigravity/backup"
LEGACY_DIR_NAMES = [".antigravity/vault"]
