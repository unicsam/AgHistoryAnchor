import os
import zipfile
import shutil
import json
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Styling ---
COLOR_SUCCESS = "#2ecc71"
COLOR_INFO = "#3498db"
COLOR_RESET = "white"

def carrier_main():
    root = tk.Tk()
    root.withdraw()
    
    # 1. Identify Payload
    # When running as an EXE, sys.executable is the path to the EXE.
    # When running as a script (for testing), __file__ is the path.
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    
    messagebox.showinfo("⚓ AgHistory Carrier", 
                        "Welcome to the High-Fidelity Standalone Restore.\n\n"
                        "This tool will automatically prepare your project folder and restore your conversation history.")
    
    # 2. Pick Destination
    parent_dest = filedialog.askdirectory(title="Select Destination Folder (Project folder will be created inside)")
    if not parent_dest:
        return print("Aborted.")

    # 3. Read Manifest from ZIP
    # In the assembled EXE, the ZIP is appended to the carrier.
    try:
        with zipfile.ZipFile(exe_path, 'r') as z:
            with z.open('manifest.json') as f:
                manifest = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Could not read internal manifest: {e}")
        return

    p_name = manifest.get("project_name", "Restored_Project")
    git_url = manifest.get("git_remote", "UNKNOWN")
    export_mode = manifest.get("export_mode", "hybrid")
    
    # Final destination is parent_dest + project_name
    final_dest = os.path.join(parent_dest, p_name)
    
    if os.path.exists(final_dest):
        if not messagebox.askyesno("Folder Exists", f"The folder [{p_name}] already exists.\n\nOverwrite contents?"):
            return print("Aborted.")
    else:
        os.makedirs(final_dest)

    print(f"[*] Preparing Project: {p_name} at {final_dest}")
    
    # 4. Git vs Files Logic
    success = False
    if export_mode in ["hybrid", "surgical"] and git_url != "UNKNOWN":
        print(f"[*] Attempting Git Clone from {git_url}...")
        try:
            # We clone into a temp subfolder or directly if empty
            # For simplicity, we clone and move
            subprocess.run(["git", "clone", git_url, "."], cwd=final_dest, check=True)
            success = True
        except Exception as e:
            print(f"[!] Git Clone failed: {e}")
            if export_mode == "surgical":
                messagebox.showerror("Error", "Surgical Mode requires Git, but clone failed. Aborting.")
                return

    if not success and export_mode in ["hybrid", "offline"]:
        print(f"[*] Extracting bundled project files...")
        try:
            with zipfile.ZipFile(exe_path, 'r') as z:
                # We want to extract everything EXCEPT the manifest and backup data first?
                # Actually, extractall is fine, we'll overwrite as needed.
                z.extractall(final_dest)
            success = True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract bundled files: {e}")
            return

    # 5. Injection Prep
    # Ensure the backup data is extracted to the right place (.antigravity/backup)
    # The ZIP already has the structure .antigravity/backup/...
    # So a simple extractall handled it if we were lucky.
    # But let's be explicit for the tool itself.
    try:
        with zipfile.ZipFile(exe_path, 'r') as z:
            z.extractall(final_dest)
    except: pass

    # 6. Final Step: Launch Restore Flow
    messagebox.showinfo("Ready", f"Project prepared successfully!\n\nLaunching AgHistoryAnchor to inject history...")
    
    try:
        # Check if Python is available to run the script
        # If the carrier was built with PyInstaller and included the tool, 
        # we could run it directly, but for now we assume Python is on the target.
        # IMPROVEMENT: If we wanted TRUE standalone, we'd have bundled the Navigator logic here.
        script_path = os.path.join(final_dest, "AgHistoryAnchor.py")
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable if "python" in sys.executable else "python", script_path, "--restore", "--live"], 
                             cwd=final_dest, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            messagebox.showwarning("Manual Action Required", "Could not find AgHistoryAnchor.py in the restored folder.\n\nPlease run it manually to finish restoration.")
    except Exception as e:
        messagebox.showerror("Execution Error", f"Failed to launch restoration script: {e}")

if __name__ == "__main__":
    carrier_main()
