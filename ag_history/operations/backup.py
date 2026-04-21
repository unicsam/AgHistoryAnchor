import os
import json
import base64
import shutil
from datetime import datetime
from ..ui.colors import UI
from ..config import BACKUP_DIR_NAME, CONVERSATIONS_DIR, BRAIN_DIR
from ..core.database import extract_workspace_uri
from ..core.utils import uri_to_path

def run_vault(navigator, matches, target_uri=None, auto=False):
    if not matches:
        if not auto: UI.warn("Nothing to anchor.")
        return
        
    target_path = uri_to_path(target_uri) if target_uri else navigator.script_dir
    
    if not auto:
        UI.header("HISTORY ANCHOR PREVIEW")
        print(f"Anchor Root: {UI.BOLD}{target_path}{UI.RESET}")
        navigator.render_tree(matches, target_path)
        if input(f"\nProceed with anchoring? [y/N]: ").strip().lower() != 'y': return

    v_base = os.path.join(target_path, BACKUP_DIR_NAME)
    v_index_path = os.path.join(v_base, "history_index.json")
    v_index = {}
    if os.path.exists(v_index_path):
        try:
            with open(v_index_path, 'r', encoding='utf-8') as f: v_index = json.load(f)
        except: pass

    for uid in matches:
        if navigator.sim_mode: UI.sim(f"Would archive: {navigator.titles.get(uid, uid[:8])}")
        else:
            title = navigator.titles.get(uid, uid[:8])
            print(f"  {UI.GREEN}[Copying]{UI.RESET} {title[:60]}...")
            
            traj_b64 = ""
            if uid in navigator.sessions:
                traj_b64 = base64.b64encode(navigator.sessions[uid]).decode('utf-8')
            
            v_index[uid] = {
                "title": title,
                "anchored_at": datetime.now().isoformat(),
                "trajectory_blob": traj_b64,
            }
            for d in ["conversations", "brain"]: os.makedirs(os.path.join(v_base, d), exist_ok=True)
            
            pb_src = os.path.join(CONVERSATIONS_DIR, f"{uid}.pb")
            if os.path.exists(pb_src): shutil.copy2(pb_src, os.path.join(v_base, "conversations", f"{uid}.pb"))
            
            br_src = os.path.join(BRAIN_DIR, uid)
            if os.path.exists(br_src):
                br_dst = os.path.join(v_base, "brain", uid)
                if os.path.exists(br_dst): shutil.rmtree(br_dst)
                shutil.copytree(br_src, br_dst)
    
    if not navigator.sim_mode:
        with open(v_index_path, 'w', encoding='utf-8') as f: json.dump(v_index, f, indent=2)
        
        # Self-copying logic is now handled in the main entry point or zip export
        
        try:
            with open(os.path.join(v_base, "git_pull_project.bat"), "w", encoding="utf-8") as f:
                f.write("@echo off\necho Pulling latest changes from GitHub...\n")
                f.write("cd ..\\..\ngit pull\n")
                f.write("echo.\necho [OK] You can now safely run AgHistoryAnchor.py to restore.\npause\n")
        except: pass
            
    UI.success("Anchoring complete.")

def run_backup_all(navigator):
    UI.header("BACKUP ALL PROJECTS")
    if navigator.sim_mode:
        if input(f"This will anchor all valid local projects. Proceed with SIMULATION? [y/N]: ").strip().lower() != 'y': return
    else:
        if input(f"{UI.RED}WARNING: LIVE MODE! This will write to disk for ALL projects.{UI.RESET} Proceed? [y/N]: ").strip().lower() != 'y': return
    
    groups = {}
    for uid, blob in navigator.sessions.items():
        uri = extract_workspace_uri(blob)
        if uri and uri.startswith("file:///"):
            groups.setdefault(uri, []).append(uid)
            
    valid_groups = {}
    for uri, uids in groups.items():
        path = uri_to_path(uri)
        if os.path.isdir(path):
            valid_groups[uri] = uids
            
    if not valid_groups:
        return UI.warn("No valid local projects found.")
        
    UI.info(f"Found {len(valid_groups)} active local projects.")
    
    for uri, uids in valid_groups.items():
        path = uri_to_path(uri)
        print(f"\nProcessing {UI.BOLD}{os.path.basename(path)}{UI.RESET} ({len(uids)} sessions)")
        run_vault(navigator, uids, target_uri=uri, auto=True)
        
    UI.success("All projects backed up!")
