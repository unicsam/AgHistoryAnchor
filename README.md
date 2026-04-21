# ⚓ AgHistoryAnchor

> **Secure. Portable. High-Fidelity.** The ultimate companion for Google Antigravity IDE history management.

**AgHistoryAnchor** is a standalone, machine-agnostic tool designed to ensure your development history never stays behind. Whether you're switching machines or just want a surgical backup of your work, Anchor provides byte-accurate reconstruction of your conversation history.

---

## ✨ Key Features

*   **⚓ Machine-Agnostic Recovery**: Restore conversation history from self-contained "Anchors" (Local Backups).
*   **🧬 High-Fidelity Restoration**: Byte-accurate reconstruction of Protobuf and JSON indices.
*   **📦 One-Click Portability**: Run as a single-file executable or a modular Python package.
*   **🔍 Smart Project Search**: Automatically identifies archives in project roots or central tools directories.
*   **🎨 Premium TUI**: A sleek, professional terminal interface with vibrant color-coding.
*   **💡 Internal Help**: Dedicated usage guide accessible via Choice `[h]`.

---

## 📂 Project Structure

```text
AgHistoryAnchor/
├── AgHistoryAnchor.py      # Entry point wrapper
├── build_exe.bat           # Windows EXE build script
├── ag_anchor.ico           # Rebranded 3D Icon
├── ag_history/             # Main application package
│   ├── cli.py              # Navigator (The "Brain" of the TUI)
│   ├── config.py           # Environment & IDE path resolution
│   ├── core/               # Engine logic (Bit-manipulation & SQLite)
│   ├── operations/         # Functional logic (Backup, Restore, Export)
│   └── ui/                 # TUI Branding & ASCII styling
└── tests/                  # Unit testing suite
```

---

## 🚀 Quickstart

### 🖥️ Using the Standalone EXE (Windows)
1. **Download**: Grab the latest `AgHistoryAnchor.exe`.
2. **Drop**: Move it to your project root or a tools folder.
3. **Run**: Double-click to start managing your history instantly.

### 🐍 Using the Source
If you prefer running from source:
1. Copy `AgHistoryAnchor.py` and the `ag_history/` folder to your project.
2. Launch the script:
   ```bash
   python AgHistoryAnchor.py
   ```

---

## ⌨️ CLI Arguments

For automated workflows or quick access, AgHistoryAnchor supports direct parameters:

| Action | Flag | Description |
| :--- | :--- | :--- |
| **Backup** | `-b`, `--backup` | Anchor Current Project |
| **Backup All** | `-ba`, `--backup-all` | Anchor ALL Projects |
| **List** | `-p`, `--projects` | Open Project Browser |
| **Checkup** | `-c`, `--checkup` | Run Anchor Checkup |
| **Restore** | `-r`, `--restore` | Enter Restore Menu |
| **Export** | `-e`, `--export` | Generate Zipped Backup |
| **Live Mode** | `--live` | Run in LIVE mode |
| **Safe Mode** | `--sim` | Run in SIMULATION mode |

**Example:**
```bash
AgHistoryAnchor.exe --backup --sim
```

---

## 🛠️ Building from Source

Want to package your own version?
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller pillow
   ```
2. **Build the EXE**:
   ```bash
   ./build_exe.bat
   ```
3. Your portable executable will be ready in the `dist/` directory.

---

## 🛡️ Safety & Integrity

*   **Automated Snapshots**: Anchor creates a timestamped safety copy of your global database before every operation.
*   **Simulation Mode**: Dry-run any restore or backup to verify logic before committing changes.
*   **Non-Destructive**: Intelligently merges history without overwriting healthy existing sessions.

---
*Developed for Antigravity — Zero-dependency core logic.*
