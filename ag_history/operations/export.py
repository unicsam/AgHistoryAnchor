import os
import shutil
import base64
import json
import subprocess
import sys
from datetime import datetime
from ..ui.colors import UI
from ..config import BACKUP_DIR_NAME, CONVERSATIONS_DIR, BRAIN_DIR
from ..core.utils import uri_to_path, build_workspace_dict

def run_export(navigator, cur_matches):
    UI.header("ZIPPED BACKUP EXPORT")
    print(f"[1] CURRENT Project | [2] CHOOSE from Map | [q] CANCEL")
    sel = input("Choice > ").strip().lower()
    
    t_uri, matches = None, []
    if sel == '1':
        t_uri, matches = navigator.target_uri, cur_matches
    elif sel == '2':
        u_map = navigator.run_history_map()
        idx = input("Project # ('q' to cancel) > ").strip()
        if idx.lower() == 'q': return
        if not idx.isdigit() or int(idx) not in u_map:
            return UI.error("Invalid choice.")
        t_uri = u_map[int(idx)]
        from ..core.database import extract_workspace_uri
        matches = [u for u, b in navigator.sessions.items() if extract_workspace_uri(b) == t_uri]
    else:
        return UI.info("Export aborted (invalid or empty selection).")
    
    target_path = uri_to_path(t_uri)
    target_name = os.path.basename(target_path)
    
    git_url = "UNKNOWN"
    try:
        git_url = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=target_path, text=True).strip()
    except: pass
    
    kit_dir = os.path.join(target_path, f"{target_name}_Zipped_Backup")
    if navigator.sim_mode: return UI.sim(f"Would create Zipped Backup at {kit_dir}")

    # --- Final LIVE Confirmation ---
    print(f"\n{UI.ORANGE}[!] WARNING: You are about to EXPORT [{target_name}] in LIVE MODE.{UI.RESET}")
    final_confirm = input(f"{UI.BOLD}[?] ARE YOU SURE YOU WANT TO PROCEED?{UI.RESET} (Type 'y' to start, or any other key to ABORT): ").strip().lower()
    if final_confirm not in ['y', 'yes']:
        return UI.info("Export aborted by user.")

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
    src_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    UI.info("INSTRUCTION: Copy the .zip to your new PC, extract it, and run setup_project.bat while Antigravity is CLOSED.")
    input(f"\n{UI.BOLD}Press Enter to return to menu...{UI.RESET}")

def run_exe_export(navigator, cur_matches):
    UI.header("SELF-ANCHORING EXE EXPORT")
    
    print(f"[1] CURRENT Project | [2] CHOOSE from Map | [q] CANCEL")
    sel = input("Choice > ").strip().lower()
    
    t_uri, matches = None, []
    if sel == '1':
        t_uri, matches = navigator.target_uri, cur_matches
    elif sel == '2':
        u_map = navigator.run_history_map()
        idx = input("Project # ('q' to cancel) > ").strip()
        if idx.lower() == 'q': return
        if not idx.isdigit() or int(idx) not in u_map:
            return UI.error("Invalid choice.")
        t_uri = u_map[int(idx)]
        from ..core.database import extract_workspace_uri
        matches = [u for u, b in navigator.sessions.items() if extract_workspace_uri(b) == t_uri]
    else:
        return UI.info("Export aborted (invalid or empty selection).")

    target_path = uri_to_path(t_uri)
    target_name = os.path.basename(target_path)
    final_exe = os.path.join(target_path, f"{target_name}_SelfAnchoring_Backup.exe")

    # --- Export Strategy Selection ---
    UI.header("EXPORT STRATEGY")
    print(f"  {UI.BOLD}[1] Hybrid{UI.RESET}   - Bundles Git Link + Project Files (Safest)")
    print(f"  {UI.BOLD}[2] Surgical{UI.RESET} - Bundles Git Link Only (Smallest EXE)")
    print(f"  {UI.BOLD}[3] Offline{UI.RESET}  - Bundles Project Files Only (No Git required)")
    
    strat = input(f"\nChoice [1] > ").strip() or "1"
    export_mode = "hybrid"
    if strat == "2": export_mode = "surgical"
    elif strat == "3": export_mode = "offline"

    if navigator.sim_mode:
        UI.sim(f"Targeting: {target_path}")
        UI.sim(f"Strategy: {export_mode.upper()}")
        UI.sim(f"Would assemble Standalone EXE at: {final_exe}")
        return UI.success("Simulation complete. Toggle [m] to run LIVE.")

    # --- Final LIVE Confirmation ---
    print(f"\n{UI.ORANGE}[!] WARNING: You are about to EXPORT [{target_name}] in LIVE MODE ({export_mode.upper()}).{UI.RESET}")
    final_confirm = input(f"{UI.BOLD}[?] ARE YOU SURE YOU WANT TO PROCEED?{UI.RESET} (Type 'y' to start, or any other key to ABORT): ").strip().lower()
    if final_confirm not in ['y', 'yes']:
        return UI.info("Export aborted by user.")

    temp_pack = os.path.join(target_path, "_tmp_pack_anchor")
    if os.path.exists(temp_pack): shutil.rmtree(temp_pack)
    os.makedirs(temp_pack)
    
    git_url = "UNKNOWN"
    try:
        git_url = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=target_path, text=True).strip()
    except: pass

    # --- Conditional Project Sweeper ---
    if export_mode in ["hybrid", "offline"]:
        UI.info(f"Sweeping project code ({export_mode})...")
        exclude = {".git", ".venv", "__pycache__", "dist", "build", ".antigravity", "_tmp_pack_anchor"}
        for item in os.listdir(target_path):
            if item in exclude: continue
            s = os.path.join(target_path, item)
            d = os.path.join(temp_pack, item)
            if os.path.isdir(s): shutil.copytree(s, d)
            else: shutil.copy2(s, d)
    else:
        UI.info("Skipping project code sweep (Surgical Mode).")

    v_base = os.path.join(temp_pack, BACKUP_DIR_NAME)
    os.makedirs(v_base, exist_ok=True)
    v_index = {}
    for uid in matches:
        traj_b64 = base64.b64encode(navigator.sessions[uid]).decode('utf-8') if uid in navigator.sessions else ""
        v_index[uid] = {
            "title": navigator.titles.get(uid, uid[:8]),
            "anchored_at": datetime.now().isoformat(),
            "trajectory_blob": traj_b64,
        }
        for d in ["conversations", "brain"]: os.makedirs(os.path.join(v_base, d), exist_ok=True)
        pb_src = os.path.join(CONVERSATIONS_DIR, f"{uid}.pb")
        if os.path.exists(pb_src): shutil.copy2(pb_src, os.path.join(v_base, "conversations", f"{uid}.pb"))
        
        b_src = os.path.join(BRAIN_DIR, uid)
        if os.path.exists(b_src): shutil.copytree(b_src, os.path.join(v_base, "brain", uid))

    with open(os.path.join(v_base, "history_index.json"), 'w', encoding='utf-8') as f: json.dump(v_index, f, indent=2)
    
    # --- STANDARD PATH RESOLUTION ---
    # root_dir is where AgHistoryAnchor.py and ag_history/ live.
    root_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # Copy tool source code into the temporary payload
    main_script = os.path.join(root_dir, "AgHistoryAnchor.py")
    if os.path.exists(main_script):
        shutil.copy2(main_script, temp_pack)
        
    core_pkg = os.path.join(root_dir, "ag_history")
    if os.path.exists(core_pkg):
        shutil.copytree(core_pkg, os.path.join(temp_pack, "ag_history"), dirs_exist_ok=True)

    with open(os.path.join(temp_pack, "manifest.json"), "w") as f:
        json.dump({
            "git_remote": git_url,
            "project_name": target_name,
            "export_mode": export_mode,
            "exported_at": datetime.now().isoformat()
        }, f)

    zip_path = os.path.join(target_path, f"{target_name}_payload.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', temp_pack)
    shutil.rmtree(temp_pack)

    # Carrier stub lookup: 
    # 1. Bundled in EXE (sys._MEIPASS)
    # 2. Project root (AgHistoryVault/)
    # 3. Scripts folder (AgHistoryVault/scripts/)
    stub_path = os.path.join(root_dir, "carrier_stub.exe")
    if not os.path.exists(stub_path):
        stub_path = os.path.join(root_dir, "scripts", "carrier_stub.exe")

    if not os.path.exists(stub_path):
        UI.warn("Carrier stub missing. Attempting to build binary (Self-Healing)...")
        try:
            carrier_src = os.path.join(root_dir, "ag_history", "operations", "carrier.py")
            subprocess.run([
                "python", "-m", "PyInstaller", "--onefile", "--noconsole",
                "--name", "carrier_stub",
                carrier_src
            ], cwd=root_dir, check=True, capture_output=True)
            
            dist_exe = os.path.join(root_dir, "dist", "carrier_stub.exe")
            if os.path.exists(dist_exe):
                shutil.move(dist_exe, stub_path)
            
            if not os.path.exists(stub_path):
                return UI.error("Auto-build failed to land carrier_stub.exe in root.")
        except Exception as e:
            return UI.error(f"Automatic build failed: {str(e)}\n\nPRO-TIP: Look in /scripts for manual build tools.")

    UI.info(f"Assembling target: {os.path.basename(final_exe)}...")
    with open(final_exe, "wb") as f_out:
        with open(stub_path, "rb") as f_stub: f_out.write(f_stub.read())
        with open(zip_path, "rb") as f_zip: f_out.write(f_zip.read())
    
    os.remove(zip_path)
    UI.success(f"Self-Anchoring EXE ready: {final_exe}")
    UI.info(f"INSTRUCTION: Copy it to your new PC and run it while Antigravity is CLOSED.")
    input(f"\n{UI.BOLD}Press Enter to return to menu...{UI.RESET}")
