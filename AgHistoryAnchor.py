import sys
import os
import argparse

# Ensure the script can find the ag_history package even if run from different locations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ag_history.cli import Navigator

def main():
    parser = argparse.ArgumentParser(description="AgHistoryAnchor: High-Fidelity IDE History Manager")
    
    # Action Flags
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', '--backup', action='store_true', help="Anchor Current Project (Backup)")
    group.add_argument('-ba', '--backup-all', action='store_true', help="Anchor ALL Projects")
    group.add_argument('-p', '--projects', action='store_true', help="Project Browser (List)")
    group.add_argument('-c', '--checkup', action='store_true', help="Anchor Checkup")
    group.add_argument('-r', '--restore', action='store_true', help="Restore from Anchor")
    group.add_argument('-e', '--export', action='store_true', help="Export Zipped Backup")
    
    # Mode Flags
    parser.add_argument('--live', action='store_true', help="Execute in LIVE mode (writes to disk)")
    parser.add_argument('--sim', '--simulation', action='store_true', help="Execute in SIMULATION mode (safe default)")
    
    args = parser.parse_args()
    
    # Resolve initial action mapping to menu keys
    initial_action = None
    if args.backup: initial_action = '1'
    elif args.backup_all: initial_action = '2'
    elif args.projects: initial_action = '3'
    elif args.checkup: initial_action = '4'
    elif args.restore: initial_action = 'r'
    elif args.export: initial_action = 'e'
    
    # Default to simulation mode unless --live is explicitly requested
    sim_mode = True
    if args.live:
        sim_mode = False
    elif args.sim:
        sim_mode = True
    
    try:
        Navigator(sim_mode=sim_mode, initial_action=initial_action).start()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
