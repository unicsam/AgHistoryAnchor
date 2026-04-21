# Antigravity History Backup and Migration Tool

> **Secure. Portable** The ultimate companion for Google Antigravity IDE for Data Migrationa and History management.

**AgHistoryAnchor** is a standalone, machine-agnostic tool designed to ensure your development history never stays behind. 

### 🚀 What it does:
*   **Saves project conversation history** into the project folder and lets you restore it at any time.
*   **Whole Project Backups**: Creates comprehensive backups (project+conversation + brain files) in ZIP form for cross-platform data migration (Linux & Windows).
*   **One-Click EXE Migration**: Generates standalone Windows executables for effortless, zero-dependency project (project + conversation + brain files) transfers. 
*   **Health Checkups**: Detects if conversations are deleted from the IDE but exist in backups, or if local backups are missing new messages from the IDE.
*   **Bulk Operations**: Lets you backup the current project or every project found in your history at once.
*   **Safety First**: Includes a read-only **Simulation Mode** to test all logic before committing changes to disk.

---

## 📂 Project Structure

A clean, organized architecture designed to separate "soul" (logic) from "body" (support files).

```text
AgHistoryAnchor/
├── AgHistoryAnchor.py      # Entry point (Main Runner)
├── ag_history/             # Main application package (The Engine)
│   ├── cli.py              # Navigator (Brain of the TUI)
│   ├── config.py           # Environment & IDE path resolution
│   ├── core/               # Engine logic (Bit-manipulation & SQLite)
│   ├── operations/         # Functional logic (Backup, Restore, Export)
│   └── ui/                 # TUI Branding & ASCII styling
├── assets/                 # Rebranded 3D Icons & Visuals
├── docs/                   # Design Proposals & Developer Guides
├── scripts/                # Build Toolkit (.bat files)
└── tests/                  # Unit testing suite
```

---

---

## 📂 Project Structure

## 🚀 Usability Guide

### 🖥️ Using the Standalone EXE (Windows)
1. **Download**: Grab the latest `AgHistoryAnchor.exe` from the `dist/` folder.
2. **Drop**: Move it to your project root or a tools folder.
3. **Run**: Double-click to start managing your history instantly.

### 🐍 Using the Source
1. Ensure `python` is installed.
2. Launch the script from the root:
   ```bash
   python AgHistoryAnchor.py
   ```

### ⌨️ Command Line Arguments
Use these for automated or rapid workflows:

| Feature | Flag | Description |
| :--- | :--- | :--- |
| **Backup Current** | `-b`, `--backup` | Anchor Current Project (`1`) |
| **Backup ALL** | `-ba`, `--backup-all` | Anchor ALL Projects (`2`) |
| **Project Browser** | `-p`, `--projects` | Open Project Browser (`3`) |
| **Checkup** | `-c`, `--checkup` | Run Anchor Checkup (`4`) |
| **Restore** | `-r`, `--restore` | Enter Restore Menu (`r`) |
| **Export Zipped** | `-e`, `--export` | Generate Zipped Backup (`e`) |
| **Export EXE** | `-x`, `--exe` | Generate Standalone EXE (`x`) |
| **Live Mode** | `--live` | Run in LIVE mode |
| **Simulation** | `--sim`, `--simulation` | Run in SAFE/SIMULATION mode |

**Example Usage:**
```powershell
# Perform a surgical backup in simulation mode
python AgHistoryAnchor.py --backup --sim

# Directly export a standalone recovery EXE in live mode
python AgHistoryAnchor.py -x --live
```
```
### 📦 High-Fidelity Recovery Strategies
When exporting a Standalone EXE (`-x`), you can choose from three intelligent strategies:

*   **1. Hybrid (Recommended)**: Bundles the Git remote link **and** the project files. The safest way to ensure recovery even if Git is unavailable on the target machine.
*   **2. Surgical**: Only bundles the Git remote link. Creates a tiny EXE (~15MB) that clones the repository on-the-fly during restoration.
*   **3. Offline**: Only bundles project files. Ideal for air-gapped environments or private repositories where Git access is not guaranteed.

### 🔄 Automated Restoration Flow
The Self-Anchoring EXE is more than an extractor—it's an installer:
1.  **Auto-Nesting**: Automatically creates a project subfolder at the destination.
2.  **Git-Aware**: Automatically pulls the latest source code if the mode supports it.
3.  **Instant Pivot**: Automatically launches the restoration menu once the project is ready, allowing for one-click history injection.

---

## 🛠️ Building & Internal Ops

### Building the Production EXE
1. **Prepare Environment**: `pip install -r requirements.txt pyinstaller`
2. **Execute Build**:
   ```powershell
   .\scripts\build_exe.bat
   ```

### Rebuilding the Carrier Stub
If you modify the restoration stub (`ag_history/operations/carrier.py`), update the base binary:
```powershell
.\scripts\build_carrier.bat
```

---

## 🛡️ Safety & Integrity

- **Automated Snapshots**: Anchor creates a timestamped safety copy of your global database before every operation.
- **Simulation Mode**: Dry-run any action to verify logic before committing changes.
- **Non-Destructive**: Merges history intelligently without overwriting healthy existing sessions.

---
> [!NOTE]
> This repository is for **Antigravity** users. Stable releases and feature updates are maintained here.

