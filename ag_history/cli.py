import sys
import os
import sqlite3
import base64
import urllib.parse
from .ui.colors import UI
from .config import GLOBAL_DB, PB_KEY, BACKUP_DIR_NAME, LEGACY_DIR_NAMES, CONVERSATIONS_DIR, BRAIN_DIR
from .core.database import extract_metadata, extract_workspace_uri
from .core.utils import normalize_uri, uri_to_path
from .operations.backup import run_vault, run_backup_all
from .operations.restore import run_restore
from .operations.export import run_export, run_exe_export
from .operations.diagnostic import run_vault_checkup

class Navigator:
    def __init__(self, sim_mode=True, initial_action=None):
        self.sim_mode = sim_mode
        self.initial_action = initial_action
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            # dirname(dirname(__file__)) because we are in ag_history/cli.py
            self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.project_name = os.path.basename(self.script_dir)
        uri_safe = self.script_dir.replace('\\', '/')
        self.target_uri = normalize_uri(f"file:///{uri_safe}")
        self.sessions, self.titles = {}, {}

    def find_vault_root(self):
        # Search for both new and legacy backup directories
        dir_names = [BACKUP_DIR_NAME] + LEGACY_DIR_NAMES
        
        checks = []
        for name in dir_names:
            checks.extend([
                os.path.join(self.script_dir, name),
                os.path.join(os.path.dirname(self.script_dir), name),
                os.path.join(os.getcwd(), name),
            ])
            
        search_bases = [self.script_dir, os.path.dirname(self.script_dir), os.getcwd()]
        for base in search_bases:
            try:
                for d in os.listdir(base):
                    full_d = os.path.join(base, d)
                    if os.path.isdir(full_d) and "Restore_Kit" in d:
                        for name in dir_names:
                            checks.append(os.path.join(full_d, name))
            except: pass

        for c in checks:
            if os.path.exists(c): return c
        return None

    def start(self):
        UI.header("AG HISTORY ANCHOR v2.4 [High-Fidelity]")
        UI.info(f"Portability Anchor: {UI.BOLD}{self.script_dir}{UI.RESET}")
        self.refresh_scan()
        
        if self.initial_action:
            self.dispatch_action(self.initial_action)
            return
            
        self.main_loop()

    def refresh_scan(self):
        UI.info("Scanning global history database...")
        if not os.path.exists(GLOBAL_DB):
            UI.error("Global database not found.")
            return
        try:
            conn = sqlite3.connect(f"file:{GLOBAL_DB}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("SELECT value FROM ItemTable WHERE key = ?", (PB_KEY,))
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                self.titles, self.sessions = extract_metadata(base64.b64decode(row[0]))
        except Exception as e: UI.error(f"Scan failed: {e}")

    def main_loop(self):
        while True:
            cur_matches = [u for u, b in self.sessions.items() if extract_workspace_uri(b) == self.target_uri]
            mode_str = f"{UI.YELLOW}SIMULATION (Safe){UI.RESET}" if self.sim_mode else f"{UI.RED}LIVE (Writes to disk){UI.RESET}"
            
            print(f"\n--- Environment ---")
            print(f"Target Project: {UI.BOLD}{self.project_name}{UI.RESET}")
            print(f"Target URI: {UI.BOLD}{self.target_uri}{UI.RESET}")
            print(f"Sessions: {UI.BOLD}{len(cur_matches)}{UI.RESET}")
            print(f"Mode: {mode_str}")
            
            print("\nMain Menu:")
            print(f"  {UI.BOLD}[1]{UI.RESET} Anchor Current Project  (Backup)")
            print(f"  {UI.BOLD}[2]{UI.RESET} Anchor ALL Projects     (Backup All)")
            print(f"  {UI.BOLD}[3]{UI.RESET} Project Browser         (List known projects)")
            print(f"  {UI.BOLD}[4]{UI.RESET} Anchor Checkup          (Compare IDE vs Local)")
            print(f"  {UI.BOLD}[r]{UI.RESET} Restore from Anchor     (Inject to IDE)")
            print(f"  {UI.BOLD}[e]{UI.RESET} Export Zipped Backup    (For another PC)")
            print(f"  {UI.BOLD}[x]{UI.RESET} Export Self-Anchoring EXE (Standalone Recovery)")
            print(f"  {UI.BOLD}[m]{UI.RESET} Toggle Mode             (Sim/Live)")
            print(f"  {UI.BOLD}[h]{UI.RESET} Help                    (Usage Guide)")
            print(f"  {UI.BOLD}[q]{UI.RESET} Quit")
            
            choice = input(f"\nChoice > ").strip().lower()
            if not self.dispatch_action(choice): break

    def dispatch_action(self, choice):
        cur_matches = [u for u, b in self.sessions.items() if extract_workspace_uri(b) == self.target_uri]
        
        if choice == '1': run_vault(self, cur_matches)
        elif choice == '2': run_backup_all(self)
        elif choice == '3': self.run_map_flow()
        elif choice == '4': run_vault_checkup(self)
        elif choice == 'r': run_restore(self)
        elif choice == 'e': run_export(self, cur_matches)
        elif choice == 'x': run_exe_export(self, cur_matches)
        elif choice == 'm': 
            self.sim_mode = not self.sim_mode
            UI.warn(f"Switched to {'SIMULATION' if self.sim_mode else 'LIVE'} mode.")
        elif choice == 'h': self.run_help_menu()
        elif choice == 'q': return False
        else:
            if self.initial_action: UI.error(f"Unknown CLI action: {choice}")
        return True

    def run_help_menu(self):
        UI.header("ANCHOR USAGE HELP")
        print(f"{UI.BOLD}Commands:{UI.RESET}")
        print(f"  [1] Backup Current  - Saves the current project's history to .antigravity/backup")
        print(f"  [2] Backup ALL      - Scans the IDE history and backs up EVERY project found.")
        print(f"  [3] Project Browser - View all projects in IDE history and anchor them by #.")
        print(f"  [4] Checkup         - Compare IDE history vs Local backups (detects stale data).")
        print(f"  [r] Restore         - Re-inject anchored sessions back into the IDE.")
        print(f"  [e] Export Zip      - Create a standalone 'Restore Kit' for moving to a new PC.")
        print(f"  [m] Toggle Mode     - Switch between SIMULATION (safe) and LIVE (write) mode.")
        
        print(f"\n{UI.BOLD}Direct CLI Parameters (Run via CMD/Terminal):{UI.RESET}")
        print(f"  --backup / -b        - Run Option [1]")
        print(f"  --backup-all / -ba   - Run Option [2]")
        print(f"  --projects / -p      - Run Option [3]")
        print(f"  --checkup / -c       - Run Option [4]")
        print(f"  --restore / -r       - Run Option [r]")
        print(f"  --export / -e        - Run Option [e]")
        print(f"  --live / --sim       - Set Mode immediately")
        
        input(f"\n{UI.BOLD}Press Enter to return...{UI.RESET}")

    def render_tree(self, uids, base_path, is_restore=False):
        for i, uid in enumerate(uids):
            is_last = (i == len(uids) - 1)
            p = "  └──" if is_last else "  ├──"
            sp = "      " if is_last else "  │   "
            title = self.titles.get(uid, f"Session {uid[:8]}")
            print(f"{p} {UI.GREEN}[Session]{UI.RESET} {title}")
            
            pb_rel = f"conversations/{uid}.pb"
            br_rel = f"brain/{uid}"
            
            if is_restore:
                pb_path = os.path.join(base_path, "conversations", f"{uid}.pb")
                br_path = os.path.join(base_path, "brain", uid)
            else:
                pb_path = os.path.join(CONVERSATIONS_DIR, f"{uid}.pb")
                br_path = os.path.join(BRAIN_DIR, uid)

            pb_ok = os.path.exists(pb_path)
            br_ok = os.path.exists(br_path)
            
            pb_status = UI.GREEN + "[✓]" + UI.RESET if pb_ok else UI.RED + "[✗]" + UI.RESET
            br_status = UI.GREEN + "[✓]" + UI.RESET if br_ok else UI.RED + "[✗]" + UI.RESET
            
            print(f"{sp}├── {pb_status} {UI.BLUE}[DB Entry]{UI.RESET} {pb_rel}")
            print(f"{sp}└── {br_status} {UI.BLUE}[Metadata]{UI.RESET} {br_rel}")

    def run_map_flow(self):
        u_map = self.run_history_map()
        if u_map:
            idx = input(f"\n{UI.BOLD}Enter Project # to Anchor ('q' to cancel): {UI.RESET}").strip()
            if idx.lower() == 'q': return
            if idx.isdigit() and int(idx) in u_map:
                t_uri = u_map[int(idx)]
                m = [u for u, b in self.sessions.items() if extract_workspace_uri(b) == t_uri]
                run_vault(self, m, t_uri)

    def run_history_map(self):
        UI.header("PROJECT BROWSER")
        groups = {}
        for uid, blob in self.sessions.items():
            uri = extract_workspace_uri(blob)
            if uri:
                if uri not in groups: groups[uri] = []
                groups[uri].append(uid)
        u_map = {}
        for idx, uri in enumerate(sorted(groups.keys()), 1):
            u_map[idx] = uri
            is_backed_up = False
            path = uri_to_path(uri)
            # Check for backup dir (new or legacy)
            is_backed_up = False
            for name in [BACKUP_DIR_NAME] + LEGACY_DIR_NAMES:
                v_dir = os.path.join(path, name)
                if os.path.isdir(v_dir) and (os.path.exists(os.path.join(v_dir, "history_index.json")) or os.path.exists(os.path.join(v_dir, "vault_index.json"))):
                    is_backed_up = True
                    break
                
            status_tag = f" {UI.GREEN}[Anchored]{UI.RESET}" if is_backed_up else ""
            print(f"  [{idx}] {os.path.basename(urllib.parse.unquote(uri).rstrip('/'))}{status_tag} -> {uri}")
        return u_map
