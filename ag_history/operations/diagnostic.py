import os
import json
from ..ui.colors import UI
from ..config import BACKUP_DIR_NAME, CONVERSATIONS_DIR, LEGACY_DIR_NAMES
from ..core.database import extract_workspace_uri
from ..core.utils import uri_to_path, calculate_file_hash

def run_vault_checkup(navigator):
    UI.header("ANCHOR STATUS: DIAGNOSTIC TREE")
    UI.info("Analyzing IDE history vs. Local Backups...")
    
    ide_groups = {}
    for uid, blob in navigator.sessions.items():
        uri = extract_workspace_uri(blob)
        if uri and uri.startswith("file:///"):
            ide_groups.setdefault(uri, []).append(uid)
    
    all_uris = sorted(ide_groups.keys())
    if not all_uris:
        return UI.warn("No projects found in IDE history.")

    for uri in all_uris:
        path = uri_to_path(uri)
        if not os.path.isdir(path): continue
        
        project_name = os.path.basename(path)
        
        # Search for backup dir
        v_dir = None
        v_index_path = None
        for name in [BACKUP_DIR_NAME] + LEGACY_DIR_NAMES:
            test_dir = os.path.join(path, name)
            test_index = os.path.join(test_dir, "history_index.json")
            if not os.path.exists(test_index):
                test_index = os.path.join(test_dir, "vault_index.json")
            
            if os.path.exists(test_index):
                v_dir = test_dir
                v_index_path = test_index
                break
        
        v_index = {}
        
        if os.path.exists(v_index_path):
            try:
                with open(v_index_path, 'r', encoding='utf-8') as f: v_index = json.load(f)
            except: pass
        
        ide_uids = set(ide_groups.get(uri, []))
        vault_uids = set(v_index.keys())
        all_uids = sorted(ide_uids | vault_uids)
        
        status_summary = ""
        if not v_dir: status_summary = f" {UI.BRED}(Unprotected){UI.RESET}"
        elif ide_uids.issubset(vault_uids): status_summary = f" {UI.GREEN}(Full Backup){UI.RESET}"
        
        print(f"\n{UI.BOLD}📁 {project_name}{UI.RESET}{status_summary}")
        print(f"  {UI.BLUE}Path:{UI.RESET} {path}")
        
        for i, uid in enumerate(all_uids):
            is_last = (i == len(all_uids) - 1)
            pref = "  └──" if is_last else "  ├──"
            title = navigator.titles.get(uid) or v_index.get(uid, {}).get("title") or f"Session {uid[:8]}"
            
            color, status_text = UI.RESET, ""
            in_ide, in_vault = uid in ide_uids, uid in vault_uids
            
            if in_ide and in_vault:
                ide_pb = os.path.join(CONVERSATIONS_DIR, f"{uid}.pb")
                vault_pb = os.path.join(v_dir, "conversations", f"{uid}.pb")
                if calculate_file_hash(ide_pb) == calculate_file_hash(vault_pb):
                    color, status_text = UI.GREEN, "[SAFE]"
                else:
                    color, status_text = UI.ORANGE, "[UPDATE REQ]"
            elif in_ide:
                color, status_text = UI.BRED, "[UNSAVED]"
            elif in_vault:
                color, status_text = UI.YELLOW, "[ARCHIVED]"
            
            print(f"{pref} {color}{status_text.ljust(12)}{UI.RESET} {title}")

    UI.info("\nLegend:")
    print(f"  {UI.GREEN}[SAFE]{UI.RESET}       - Fully backed up and matching.")
    print(f"  {UI.ORANGE}[UPDATE REQ]{UI.RESET}- IDE has new data not in backup.")
    print(f"  {UI.BRED}[UNSAVED]{UI.RESET}    - Exists in IDE only (Not backed up).")
    print(f"  {UI.YELLOW}[ARCHIVED]{UI.RESET}   - Exists in Backup only (Deleted from IDE).")
