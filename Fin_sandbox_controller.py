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
    run(f'"{vbox}" controlvm "{vm}" keyboardputscancode {code}')
    time.sleep(0.05)

def press_enter(vbox, vm):
    send_scancode(vbox, vm, "1C")
    send_scancode(vbox, vm, "9C")

def type_digits(vbox, vm, digits):
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
    
    time.sleep(5)    

    press_enter(vbox, vm)     
    time.sleep(0.5)

    type_digits(vbox, vm, "123")  
    time.sleep(0.5)

    press_enter(vbox, vm)    

    print("[+] Login keys sent. Waiting for desktop...")
    time.sleep(25)           

def type_text(vbox, vm, text):
    for ch in text:
        run(f'"{vbox}" controlvm "{vm}" keyboardputstring "{ch}"')
        time.sleep(0.12)  


def press_super(vbox, vm):
    
    send_scancode(vbox, vm, "e0")
    send_scancode(vbox, vm, "5b")
    send_scancode(vbox, vm, "e0")
    send_scancode(vbox, vm, "db")



def run_analyzer_inside_vm(vbox, vm, url):
    print("[+] Running analyzer inside VM (GUI automation)...")

    press_super(vbox, vm)
    time.sleep(1)

    type_text(vbox, vm, "terminal")
    time.sleep(0.5)

    press_enter(vbox, vm)
    print("[+] Terminal should be opening...")
    time.sleep(5)

    cmd = f'python3 analyze_url.py "{url}"'
    print(f"[+] Typing command: {cmd}")
    type_text(vbox, vm, cmd)
    time.sleep(1)

    press_enter(vbox, vm)
    print("[+] Analyzer command entered.")



def shutdown_vm(vbox, vm):
    print("[+] Shutting down VM...")
    run(f'"{vbox}" controlvm "{vm}" acpipowerbutton')
    time.sleep(10)
    run(f'"{vbox}" controlvm "{vm}" poweroff')

def retrieve_results(vbox, vm):
    print("[+] Retrieving analysis results...")

    files = [ "report.txt"]

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

    auto_login(vbox, vm)
    time.sleep(8)

    print("[+] Analyzing URL inside VM...")
    run_analyzer_inside_vm(vbox, vm, url)
    retrieve_results(vbox, vm)


    time.sleep(50)
    


    shutdown_vm(vbox, vm)


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
