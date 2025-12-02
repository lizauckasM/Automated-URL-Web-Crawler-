Implementation Guidelines for Automated Web Crawler Sandbox Analysis
Michael 
1. Environment Setup
•	Python:
Ensure you have Python 3.8 or higher installed on your host machine.
•	Python dependencies:
Install required Python packages by running:
pip install playwright
playwright install
•	VirtualBox:
 Install Oracle VirtualBox on your host machine. This is necessary to run the virtual machine sandbox.
2. Virtual Machine Preparation (Should be included from installation)
•	VM Snapshot:
 Import the provided VirtualBox VM snapshot named CleanSnapshot into VirtualBox.
•	VM Configuration:
o	The VM should have a working internet connection via NAT or host-only adapter.
o	Firefox and Python must be installed inside the VM.
o	Ensure the VM snapshot is clean and ready for malware testing.
•	Purpose of the VM
The VM is not used for instrumentation or monitoring.
It serves as a visual sandbox showing how the page loads in a real Firefox session, but:
o	No tracking of VM activity occurs
o	No interaction between VM Firefox and analyzer
o	No VM network data is collected
o	The real analysis happens on the host, not in the VM.
3. Running the Analysis
•	Sandbox Controller Script:
 Use the sandbox_controller.py script on the host machine to automate VM management:
o	Restores the VM snapshot to a clean state
o	Starts the VM in GUI mode
o	Logs into the VM automatically
o	Opens Firefox inside the VM and navigates to the target URL
•	Launching the Real Analyzer
o	While the VM is loading the page, the controller also launches:
python analyze_url.py <url>
•	Command to launch sandbox controller:
python sandbox_controller.py <url>
or
python analyze_url.py "https://example.com"
Replace <url> with the website you want to analyze (e.g., https://example.com).
•	Automated Browser Interaction:
 Script sends keyboard inputs to open Firefox and navigate to the URL inside the VM.
•	URL Analysis Script:
 Inside the VM, analyze_url.py runs using Playwright to:
o	Record domains contacted by the page
o	Track redirects and popups
o	Capture console errors and automatic downloads
o	Produce a detailed JSON report (analysis.json)
•	Duration:
The system waits and interacts with the page for around 40 seconds to catch delayed behaviors.
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
•	Playwright analysis runs on the host
o	Not sandboxed, not isolated.
•	The VM is currently non-functional for detection
o	It is only a visual layer, not an analysis framework.
•	If a malicious site exploits Firefox inside the VM
o	The host remains safe, but the analyzer will not detect the exploit because its Playwright instance runs separately.
•	True sandboxing would require:
o	Running Playwright inside the VM
o	Or tracking VM traffic, syscalls, and browser activity, Neither of which is implemented yet.
