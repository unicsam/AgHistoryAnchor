# AgHistoryAnchor Developer Guide: Internal Architecture

This document provides a detailed technical breakdown of the **AgHistoryAnchor** architecture for developers maintaining or extending the tool.

## 1. High-Level Core Logic
The program operates as a standalone manager for the Antigravity IDE's conversation history. It bridges the gap between the IDE's internal SQLite database (`state.vscdb`) and a project-specific "Anchor" (`.antigravity/backup`).

### Modular Architecture (v2.4+)
As of v2.4, the project is organized into a modular package structure to improve maintainability and testability:

- **`AgHistoryAnchor.py`**: Thin entry point wrapper.
- **`ag_history/`**: Main package.
  - **`config.py`**: Centralized environment detection and SQLite keys.
  - **`core/`**: Deep logic (Protobuf, Database, Utils).
  - **`ui/`**: TUI rendering and branding.
  - **`operations/`**: Functional logic (Backup, Restore, Diagnostic, Export).
  - **`cli.py`**: Orchestration and Menu system.

---

## 2. Key Components

### A. The Protobuf Engine (`ag_history/core/protobuf.py`)
Implements a manual Protobuf encoder to avoid dependency on heavy libraries.
- **Surgical Selection**: The `strip_field` method allows removing specific fields (titles, URIs) from an existing blob without corruption.
- **Trajectory Recap**: Specifically rebuilds Field 9 and 17 to point the IDE to the current project's path.

### B. Environment Resolution (`ag_history/config.py`)
Dynamically maps system paths for Windows and POSIX:
- **GLOBAL_DB**: User's roaming state database.
- **PB_KEY**: `antigravityUnifiedStateSync.trajectorySummaries`.

### C. Operations Suite (`ag_history/operations/`)
- **`backup.py`**: Handles single-project anchoring and "Backup All" flows.
- **`restore.py`**: Implements the "Anchor" flow—copying physical files and injecting metadata into SQLite.
- **`diagnostic.py`**: Uses file hashes to compare the IDE's live data against the Local Backup.

---

## 3. The "Anchor" Restore Flow
When a restore is triggered:
1. **Safety First**: A `state.vscdb.ag_backup_[timestamp]` is created.
2. **File Migration**: `.pb` and `brain/` files are moved to the IDE's storage.
3. **Metadata Recalibration**: 
   - Reads existing trajectory summaries.
   - Strips old workspace identifiers.
   - Injects new Field 9 (Corpus/Git) and Field 17 (Local URI) for the current path.
4. **Sidebar Sync**: Updates the JSON index for immediate UI reflection in the IDE.

---

## 4. Maintenance Notes
- **EXE Packaging**: The tool can be converted to a standalone EXE using `PyInstaller`. A `build_exe.bat` is provided.
- **Portability**: All imports within the package are relative or use `sys.path` injection to ensure the folder can be moved as a unit.
- **Standard Library Only**: NEVER add external dependencies to `ag_history/core` to maintain the "drop-in" nature of the tool.

---
*Developed for Antigravity — Modular & High-Fidelity History Preservation.*
