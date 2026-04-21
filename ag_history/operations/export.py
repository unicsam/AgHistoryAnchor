import os
import shutil
import base64
import json
import subprocess
from datetime import datetime
from ..ui.colors import UI
from ..config import BACKUP_DIR_NAME, CONVERSATIONS_DIR, BRAIN_DIR
from ..core.database import extract_workspace_uri
from ..core.utils import uri_to_path

def run_export(navigator, cur_matches):
    UI.header("ZIPPED BACKUP EXPORT")
    print(f"[1] CURRENT Project | [2] CHOOSE from Map")
    sel = input("Choice > ").strip()
    t_uri, matches = navigator.target_uri, cur_matches
    if sel == '2':
        u_map = navigator.run_history_map()
        idx = input("Project # ('q' to cancel) > ").strip()
        if idx.lower() == 'q': return
        if not idx.isdigit() or int(idx) not in u_map:
            return UI.error("Invalid choice.")
        t_uri = u_map[int(idx)]
        matches = [u for u, b in navigator.sessions.items() if extract_workspace_uri(b) == t_uri]
    
    target_path = uri_to_path(t_uri)
    target_name = os.path.basename(target_path)
    
    git_url = "UNKNOWN"
    try:
        git_url = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=target_path, text=True).strip()
    except: pass
    
    kit_dir = os.path.join(target_path, f"{target_name}_Zipped_Backup")
    if navigator.sim_mode: return UI.sim(f"Would create Zipped Backup at {kit_dir}")

    os.makedirs(kit_dir, exist_ok=True)
    v_base = os.path.join(kit_dir, BACKUP_DIR_NAME)
    v_index = {}
    for uid in matches:
        traj_b64 = ""
        if uid in navigator.sessions:
            traj_b64 = base64.b64encode(navigator.sessions[uid]).decode('utf-8')
        
        v_index[uid] = {
            "title": navigator.titles.get(uid, uid[:8]),
            "anchored_at": datetime.now().isoformat(),
            "trajectory_blob": traj_b64,
        }
        for d in ["conversations", "brain"]: os.makedirs(os.path.join(v_base, d), exist_ok=True)
        pb_src = os.path.join(CONVERSATIONS_DIR, f"{uid}.pb")
        if os.path.exists(pb_src):
            shutil.copy2(pb_src, os.path.join(v_base, "conversations", f"{uid}.pb"))

        b_src = os.path.join(BRAIN_DIR, uid)
        if os.path.exists(b_src):
            b_dst = os.path.join(v_base, "brain", uid)
            if os.path.exists(b_dst): shutil.rmtree(b_dst)
            shutil.copytree(b_src, b_dst)
    
    with open(os.path.join(v_base, "history_index.json"), 'w', encoding='utf-8') as f: json.dump(v_index, f, indent=2)
    
    # Export the whole tool package
    src_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shutil.copy2(os.path.join(src_root, "AgHistoryAnchor.py"), kit_dir)
    shutil.copytree(os.path.join(src_root, "ag_history"), os.path.join(kit_dir, "ag_history"), dirs_exist_ok=True)
    
    with open(os.path.join(kit_dir, "setup_project.bat"), "w", encoding='utf-8') as f:
        f.write(f"@echo off\necho ====================================================\n")
        f.write(f"echo  ANCHOR: RESTORE SETUP\n")
        f.write(f"echo ====================================================\n")
        f.write(f"git clone {git_url} {target_name}\n")
        f.write(f"xcopy /E /I /Y \".antigravity\" \"{target_name}\\.antigravity\"\n")
        f.write(f"xcopy /E /I /Y \"ag_history\" \"{target_name}\\ag_history\"\n")
        f.write(f"move \"AgHistoryAnchor.py\" \"{target_name}\\AgHistoryAnchor.py\"\n")
        f.write(f"echo.\n")
        f.write(f"echo [OK] Ready. Run AgHistoryAnchor.py in the new project folder.\n")
        f.write(f"pause\n")
        
    shutil.make_archive(kit_dir, 'zip', kit_dir)
    UI.success(f"Backup Zipped successfully: {kit_dir}.zip")
