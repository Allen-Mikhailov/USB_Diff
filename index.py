#!/usr/bin/env python3
import os
import subprocess
import time
import sys

# ANSI Escape Codes for Terminal Colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def get_usb_devices():
    """Runs lsusb and returns a set of device strings."""
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
        return {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except FileNotFoundError:
        print("Error: 'lsusb' command not found.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running lsusb: {e}", file=sys.stderr)
        sys.exit(1)

def get_dev_nodes():
    """Scans the /dev directory and returns a set of absolute paths to device nodes."""
    try:
        nodes = set()
        for root, dirs, files in os.walk('/dev'):
            for name in files + dirs:
                nodes.add(os.path.join(root, name))
        return nodes
    except Exception as e:
        print(f"Error scanning /dev: {e}", file=sys.stderr)
        sys.exit(1)

def monitor_usb_and_dev():
    print(f"{BOLD}Initializing baseline for lsusb and /dev...{RESET}")
    
    # Capture initial states
    current_usb = get_usb_devices()
    current_dev = get_dev_nodes()
    
    print(f"Monitoring started.")
    print(f"  Initial USB devices: {len(current_usb)}")
    print(f"  Initial /dev nodes:  {len(current_dev)}")
    print("Press Ctrl+C to stop.\n")
    print("-" * 60)

    try:
        while True:
            time.sleep(1)  # Scan interval
            
            # Fetch fresh states
            new_usb = get_usb_devices()
            new_dev = get_dev_nodes()

            # Check for changes
            usb_added = new_usb - current_usb
            usb_removed = current_usb - new_usb

            dev_added = new_dev - current_dev
            dev_removed = current_dev - new_dev

            # Print changes if any occurred
            if usb_added or usb_removed or dev_added or dev_removed:
                
                # Print lsusb changes
                for dev in usb_added:
                    print(f"{GREEN}[+] USB ADDED:    {dev}{RESET}")
                for dev in usb_removed:
                    print(f"{RED}[-] USB REMOVED:  {dev}{RESET}")

                # Print /dev changes
                for node in sorted(dev_added):
                    print(f"{GREEN}[+] /dev ADDED:   {node}{RESET}")
                for node in sorted(dev_removed):
                    print(f"{RED}[-] /dev REMOVED: {node}{RESET}")
                
                print("-" * 60)

                # Update baselines
                current_usb = new_usb
                current_dev = new_dev

    except KeyboardInterrupt:
        print(f"\n{BOLD}Monitoring stopped.{RESET}")

if __name__ == "__main__":
    monitor_usb_and_dev()
