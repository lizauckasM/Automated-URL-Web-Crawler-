import subprocess
import time
import os
import sys

#Example terminal code: python sandbox_controller.py "google.com"

SNAPSHOT = "CleanSnapshot"
REPORT_FILE = "sandbox_report.txt"

def run(cmd):
    print(f"[cmd] {cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def find_vboxmanage():
    paths = [
        r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
        r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            print(f"[+] Found VBoxManage: {p}")
            return p
    print("[!] VBoxManage not found.")
    sys.exit(1)

def detect_vm(vbox):
    out, err, code = run(f'"{vbox}" list vms')
    if code != 0 or out.strip() == "":
        print("[!] No VMs found.")
        sys.exit(1)

    print("[+] Available VMs:")
    print(out)

    # Look for SEED4  
    for line in out.splitlines():
        if "SEED2" in line:
            vm_name = line.split('"')[1]
            print(f"[+] Using VM: {vm_name}")
            return vm_name

    print("[!] SEED3 not found. Check VM names with VBoxManage list vms")
    sys.exit(1)


def restore_snapshot(vbox, vm):
    print("[+] Restoring snapshot...")
    run(f'"{vbox}" controlvm "{vm}" poweroff')
    time.sleep(1)
    run(f'"{vbox}" snapshot "{vm}" restore "{SNAPSHOT}"')

def start_vm(vbox, vm):
    print("[+] Starting VM GUI...")
    run(f'"{vbox}" startvm "{vm}" --type gui')

def send_scancode(vbox, vm, code):
    # VirtualBox scancode sender (make + break)
    run(f'"{vbox}" controlvm "{vm}" keyboardputscancode {code}')
    time.sleep(0.05)

def press_enter(vbox, vm):
    # Enter key: make=1C, break=9C
    send_scancode(vbox, vm, "1C")
    send_scancode(vbox, vm, "9C")

def type_digits(vbox, vm, digits):
    # Scancodes for numbers
    SC = {
        "1": ("02", "82"),
        "2": ("03", "83"),
        "3": ("04", "84"),
    }
    for d in digits:
        make, brk = SC[d]
        send_scancode(vbox, vm, make)
        send_scancode(vbox, vm, brk)

def auto_login(vbox, vm):
    print("[+] Attempting auto-login with password: 123")
    
    time.sleep(5)   # Wait for login screen to finish drawing

    press_enter(vbox, vm)    # activate password field
    time.sleep(0.5)

    type_digits(vbox, vm, "123")  # type password
    time.sleep(0.5)

    press_enter(vbox, vm)    # submit login

    print("[+] Login keys sent. Waiting for desktop...")
    time.sleep(25)           # allow desktop to load

def type_text(vbox, vm, text):
    """
    Very safe typer that uses VirtualBox keyboardputstring.
    Works with spaces, symbols, URLs, everything.
    """
    for ch in text:
        run(f'"{vbox}" controlvm "{vm}" keyboardputstring "{ch}"')
        time.sleep(0.12)  # slow to avoid dropped characters


def press_super(vbox, vm):
    # Left GUI key: make = e0 5b, break = e0 db
    send_scancode(vbox, vm, "e0")
    send_scancode(vbox, vm, "5b")
    send_scancode(vbox, vm, "e0")
    send_scancode(vbox, vm, "db")


def launch_firefox_keyboard(vbox, vm, url):
    print("[+] Launching Firefox using keyboard…")
    
    # Open application search (press Windows key)
    press_super(vbox, vm)
    time.sleep(1)

    # Type "firefox"
    type_text(vbox, vm, "firefox")
    time.sleep(0.5)

    # Press Enter to open Firefox
    press_enter(vbox, vm)
    print("[+] Firefox should be opening…")
    time.sleep(4)

    # Type URL in Firefox address bar
    type_text(vbox, vm, url)
    time.sleep(0.3)

    # Press Enter to load the page
    press_enter(vbox, vm)
    print("[+] URL entered.")

def launch_firefox_via_terminal(vbox, vm, url):
    print("[+] Launching Firefox via Terminal...")

    # Press Windows key to open app search
    press_super(vbox, vm)
    time.sleep(1)

    # Type "terminal"
    type_text(vbox, vm, "terminal")
    time.sleep(0.5)

    # Press Enter to open Terminal
    press_enter(vbox, vm)
    print("[+] Terminal should be opening...")
    time.sleep(5)  # Wait for terminal to open

    # Type the firefox command with DISPLAY=:0 and URL
    cmd = f'DISPLAY=:0 firefox "{url}" &'
    print(f"[+] Typing command: {cmd}")
    type_text(vbox, vm, cmd)
    time.sleep(1.0)


    # Press Enter to run the command
    press_enter(vbox, vm)
    print("[+] Firefox launch command entered.")

def run_analyzer_inside_vm(vbox, vm, url):
    print("[+] Running analyzer inside VM (GUI automation)...")

    # Open application launcher
    press_super(vbox, vm)
    time.sleep(1)

    # Type terminal
    type_text(vbox, vm, "terminal")
    time.sleep(0.5)

    # Open terminal
    press_enter(vbox, vm)
    print("[+] Terminal should be opening...")
    time.sleep(5)

    # Run analyzer from shared folder or host path
    cmd = f'python3 analyze_url.py "{url}"'
    print(f"[+] Typing command: {cmd}")
    type_text(vbox, vm, cmd)
    time.sleep(1)

    press_enter(vbox, vm)
    print("[+] Analyzer command entered.")


import subprocess

def record_activity(duration=20, url=None):
    print(f"[+] Recording activity for {duration} seconds...")

    # ───────────────────────────────────────────────
    # LAUNCH analyze_url.py IN BACKGROUND 
    # ───────────────────────────────────────────────
    if url:
        print("[+] Starting background analysis...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen(
            ["python", "analyze_url.py", url],
            cwd=script_dir
        )

    # ───────────────────────────────────────────────

    text_log = []
    for i in range(duration):
        text_log.append(f"System running... second {i}")
        time.sleep(1)

    return "\n".join(text_log)


def shutdown_vm(vbox, vm):
    print("[+] Shutting down VM...")
    run(f'"{vbox}" controlvm "{vm}" acpipowerbutton')
    time.sleep(10)
    run(f'"{vbox}" controlvm "{vm}" poweroff')

def retrieve_results(vbox, vm):
    print("[+] Retrieving analysis results...")

    files = ["analysis.json", "report.txt"]

    for f in files:
        run(
            f'"{vbox}" guestcontrol "{vm}" copyfrom '
            f'--username seed --password 123 '
            f'/home/seed/{f} .'
        )


def main():
    if len(sys.argv) != 2:
        print("Usage: python sandbox_controller.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"[+] URL to analyze: {url}")

    vbox = find_vboxmanage()
    vm = detect_vm(vbox)

    restore_snapshot(vbox, vm)
    start_vm(vbox, vm)

    print("[+] Give VM time to boot...")
    time.sleep(50)

    auto_login(vbox, vm)#login
    time.sleep(8)

    print("[+] Analyzing URL inside VM...")
    run_analyzer_inside_vm(vbox, vm, url)
    retrieve_results(vbox, vm)

    #log = record_activity(duration=40, url=url)
    time.sleep(50)
    
    #with open(REPORT_FILE, "w") as f:
        #f.write("=== Sandbox Report ===\n")
        #f.write(f"URL: {url}\n\n")
        #f.write(log)
    
    #print(f"[+] Report saved: {REPORT_FILE}")

    shutdown_vm(vbox, vm)

    # Read and print report from shared folder on host
    shared_report_path = r"C:\Users\Mick\Documents\School\Sophmore Year- S1\CS 303\Shared VM Folder\report.txt"
    try:
        with open(shared_report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        print("---- Report Content ----")
        print(report_content)
        print("-----------------------")
    except Exception as e:
        print(f"[!] Failed to read report file: {e}")



    print("[+] COMPLETE.")

if __name__ == "__main__":
    main()
