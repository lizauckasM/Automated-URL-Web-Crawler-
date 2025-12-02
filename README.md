Implementation Guidelines for Automated Web Crawler Sandbox Analysis
Michael Lizauckas
1. Environment Setup
•	Python:
Ensure you have Python 3.8 or higher installed on your host machine.
•	Windows OS
•	Python dependencies:
Install required Python packages by running:
pip install playwright
playwright install
•	VirtualBox:
 Install Oracle VirtualBox on your host machine. This is necessary to run the virtual machine sandbox.
2. Virtual Machine Preparation (Should be included from installation)
•	VM Snapshot:
 Import the provided VirtualBox VM snapshot named Clean Snapshot into VirtualBox.
•	VM Configuration:
o	The VM should have a working internet connection via NAT or host-only adapter.
o	Firefox and Python must be installed inside the VM.
o	Ensure the VM snapshot is clean and ready for malware testing.
o	Code runs on VM with Username: seed Password: 123
•	VM Requirements
o	Inside the VM:
	Python 3 installed
	Playwright installed:
pip install playwright
playwright install
o	The analysis script placed at:
	/home/seed/analyze_url.py
•	Purpose of the VM
It serves as a safe/visual sandbox showing how the page, but:
o	Is unpractical ad unsecure
o	Analysis is done in the VM and sent to a ShareFile with the host (unsecure)
3. Running the Analysis
•	Sandbox Controller Script:
 Use the sandbox_controller.py script on the host machine to automate VM management:
o	Restores the VM snapshot to a clean state
o	Starts the VM in GUI mode
o	Logs into the VM automatically
o	Opens Firefox inside the VM and navigates to the target URL
•	Launching the Real Analyzer
o	While the VM is loading the page, the controller also launches:
python analyze_url.py “URL”
•	Command to launch sandbox controller/analyzer:
python sandbox_controller.py “URL”
or
python analyze_url.py “https://example.com” (Unsafe on host)
Replace <URL> with the website you want to analyze (e.g., https://example.com).
•	Automated Browser Interaction:
Script sends keyboard inputs to open analyze script in the VM and send data back to host.
•	URL Analysis Script:
 Inside the VM, analyze_url.py runs using Playwright to:
o	Record domains contacted by the page
o	Track redirects and popups
o	Capture console errors and automatic downloads
o	Produce a detailed JSON report (analysis. Json)
•	Duration:
The system waits and interacts with the page to catch delayed behaviors.
4. Output and Interpretation
•	Reports Generated:
o	report.txt: Contains structured data about redirects, visited domains, console messages, popups, downloads, and HTTP status, a risk score and verdict (Safe, Suspicious, Malicious).
•	Risk Assessment:
 The scoring considers:
o	Number of redirects
o	Presence of popups
o	Automatic downloads
o	Number of external domains contacted
o	Console errors
•	Verdict Explanation:
o	SAFE: Low risk with minimal suspicious activity
o	SUSPICIOUS: Moderate risk indicators like multiple popups or redirects
o	MALICIOUS: High risk with automatic downloads or many popups/redirects
o	UNKNOWN: If navigating fails
Notes
•	Playwright analysis runs on the VM
o	The command sent to the VM are points of entry for an attacker
•	The VM is currently non-practical
o	It is mainly a visual layer, not very fast.
•	If a malicious site exploits inside the VM
o	The host remains safe, but attacker can break out of the VM. Additionally, at this stage the data on the VM is not wiped
•	Improvements would require:
o	A faster private VM with a preload
o	Better tracking software
o	Better scoring (possibly in combination with AI)
o	Better User interface
