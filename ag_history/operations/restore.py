import os
import sqlite3
import base64
import json
import time
import shutil
from datetime import datetime
from ..ui.colors import UI
from ..config import GLOBAL_DB, PB_KEY, JSON_KEY, CONVERSATIONS_DIR, BRAIN_DIR, BACKUP_PREFIX, BACKUP_DIR_NAME
from ..core.protobuf import ProtobufEncoder
from ..core.database import create_backup, safe_rollback, extract_metadata
from ..core.utils import build_workspace_dict

def run_restore(navigator):
    UI.header("THE ANCHOR: PRECISION RESTORE")
    v_root = navigator.find_vault_root()
    if not v_root: return UI.error("No anchored sessions found. (Checked project roots & tools)")
    
    v_base = os.path.join(v_root, "conversations")
    if not os.path.exists(v_base): return UI.error("Backup conversations directory missing.")
    
    v_files = [f for f in os.listdir(v_base) if f.endswith(".pb")]
    if not v_files: return UI.error("Anchor is empty.")
    
    v_index_path = os.path.join(v_root, "history_index.json")
    if not os.path.exists(v_index_path):
        v_index_path = os.path.join(v_root, "vault_index.json") # Legacy support
    v_index = {}
    if os.path.exists(v_index_path):
        try:
            with open(v_index_path, 'r', encoding='utf-8') as f: v_index = json.load(f)
        except: pass

    anchored_sessions = {}
    for i, f in enumerate(v_files, 1):
        uid = f[:-3]
        entry = v_index.get(uid, {})
        title = entry.get("title", f"Session {uid[:8]}")
        traj_b64 = entry.get("trajectory_blob", "")
        traj_blob = base64.b64decode(traj_b64) if traj_b64 else None
        
        mtime = os.path.getmtime(os.path.join(v_base, f))
        m_str = datetime.fromtimestamp(mtime).strftime("%b %d, %H:%M")
        
        has_traj = "[✓] metadata" if traj_blob else "[!] no metadata (will create fresh)"
        anchored_sessions[i] = (uid, title, traj_blob)
        print(f"  [{i}] {UI.BOLD}{title}{UI.RESET}")
        print(f"      {UI.BLUE}ID:{UI.RESET} {uid[:8]} | {UI.YELLOW}Saved:{UI.RESET} {m_str} | {has_traj}")

    choice = input(f"\nSelect # to Restore (or 'all', 'b' back): ").strip().lower()
    if choice == 'b': return
    to_restore = list(anchored_sessions.values()) if choice == 'all' else [anchored_sessions[int(choice)]] if choice.isdigit() and int(choice) in anchored_sessions else []
    if not to_restore: return UI.error("Invalid choice.")

    UI.info(f"Targeting {len(to_restore)} sessions for recalibration...")
    navigator.render_tree([u for u, t, b in to_restore], v_root, is_restore=True)
    
    if input(f"\nProceed with {'SIMULATION' if navigator.sim_mode else 'LIVE'} restore? [y/N]: ").strip().lower() != 'y': return

    if navigator.sim_mode:
        UI.sim(f"Recalibrate URI to: {navigator.target_uri}")
        return UI.success("Simulation complete.")

    backup_path = ""
    try:
        os.makedirs(os.path.dirname(GLOBAL_DB), exist_ok=True)
        if os.path.exists(GLOBAL_DB):
            backup_path = create_backup(GLOBAL_DB, BACKUP_PREFIX)
        
        ws_dict = build_workspace_dict(navigator.script_dir)
        
        conn = sqlite3.connect(GLOBAL_DB, timeout=10)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS ItemTable (key TEXT PRIMARY KEY, value TEXT)")
        
        cur.execute("SELECT value FROM ItemTable WHERE key = ?", (PB_KEY,))
        row = cur.fetchone()
        cur_pb = base64.b64decode(row[0]) if row and row[0] else b""
        titles_dict, blobs_dict = extract_metadata(cur_pb)
        
        cur.execute("SELECT value FROM ItemTable WHERE key = ?", (JSON_KEY,))
        j_row = cur.fetchone()
        chat_idx = json.loads(j_row[0]) if j_row and j_row[0] else {"version": 1, "entries": {}}
        
        restored_uids = set()
        for uid, title, traj_blob in to_restore:
            pb_file = os.path.join(v_root, "conversations", f"{uid}.pb")
            mtime = int(os.path.getmtime(pb_file)) if os.path.exists(pb_file) else int(time.time())
            ctime = int(os.path.getctime(pb_file)) if os.path.exists(pb_file) else mtime
            
            if os.path.exists(pb_file):
                os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
                shutil.copy2(pb_file, os.path.join(CONVERSATIONS_DIR, f"{uid}.pb"))
                UI.info(f"Copied .pb -> conversations/{uid[:8]}...")
            
            br_src = os.path.join(v_root, "brain", uid)
            if os.path.exists(br_src):
                br_dst = os.path.join(BRAIN_DIR, uid)
                if os.path.exists(br_dst): shutil.rmtree(br_dst)
                shutil.copytree(br_src, br_dst)
                UI.info(f"Copied brain -> brain/{uid[:8]}...")
            
            blobs_dict[uid] = traj_blob
            titles_dict[uid] = title
            restored_uids.add(uid)
            
            chat_idx.setdefault("entries", {})[uid] = {
                "sessionId": uid,
                "title": title,
                "lastModified": mtime * 1000,
                "isStale": False
            }

        final_pb_bytes = b""
        for b_uid, b_blob in blobs_dict.items():
            b_title = titles_dict.get(b_uid, f"Session {b_uid[:8]}")
            
            if b_uid in restored_uids:
                pb_f = os.path.join(v_root, "conversations", f"{b_uid}.pb")
                bm = int(os.path.getmtime(pb_f)) if os.path.exists(pb_f) else int(time.time())
                bc = int(os.path.getctime(pb_f)) if os.path.exists(pb_f) else bm
                final_pb_bytes += ProtobufEncoder.build_trajectory_entry(
                    b_uid, b_title, ws_dict, bc, bm, existing_inner=b_blob
                )
            else:
                final_pb_bytes += ProtobufEncoder.build_trajectory_entry(
                    b_uid, b_title, None, int(time.time()), int(time.time()), existing_inner=b_blob
                )

        encoded_pb = base64.b64encode(final_pb_bytes).decode('utf-8')
        cur.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (PB_KEY, encoded_pb))
        cur.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (JSON_KEY, json.dumps(chat_idx, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
        UI.success(f"Restore complete. {len(restored_uids)} session(s) injected.")
        if backup_path: UI.info(f"Safety Backup: {backup_path}")
        
    except Exception as e:
        if backup_path: safe_rollback(backup_path, GLOBAL_DB)
        UI.error(f"Restore failed (Rolled back): {e}")
