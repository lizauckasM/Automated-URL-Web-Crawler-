import sys
import json
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


#Usage: python analyze_url.py "https://example.com"





OUT_TXT = "report.txt"
TIMEOUT_MS = 20000  # page timeout

def normalize_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url
    return url


def domain_of(url):
    try:

        return urlparse(url).netloc
    except:
        return ""


def analyze(url):
    results = {"url": url, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "visited_domains": set(),"redirect_chain": [],"console_messages": [],"auto_download": False,"http_status": None, }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        
        def on_console(msg):
            results["console_messages"].append(f"{msg.type}: {msg.text}")
        page.on("console", on_console)

        def on_request(request):
            domain = domain_of(request.url)
            if domain:
                results["visited_domains"].add(domain)
        page.on("request", on_request)

        def on_frame_navigate(frame):
            url = frame.url
            if url not in results["redirect_chain"]:
                results["redirect_chain"].append(url)
        page.on("framenavigated", on_frame_navigate)

        results["popup_urls"] = []  
        def on_popup(popup):
            results["popup_urls"].append(popup.url)
        page.on("popup", on_popup)


        def on_download(download):
            results["auto_download"] = True
        context.on("download", on_download)

    
        try:
            url = normalize_url(url)
            response = page.goto(url, timeout=TIMEOUT_MS)


            if response:
                results["http_status"] = response.status

                
                if response:
                    results["http_status"] = response.status

        except Exception as e:
            results["console_messages"].append(f"ERROR: navigation failed: {e}")

        page.wait_for_timeout(5000)  

        

        print("[+] Running deep interaction scan...")

        
        for _ in range(5):
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(800)

        
        clickable = page.query_selector_all("a, button, div[onclick], span[onclick]")
        print(f"[+] Found {len(clickable)} clickable elements")

        for el in clickable[:12]: 
            try:
                el.click(timeout=2000)
                page.wait_for_timeout(800)  
            except:
                pass

        page.wait_for_timeout(5000)


        browser.close()

    results["visited_domains"] = list(results["visited_domains"])

    
    lines = []
    lines.append(f"Analysis report for: {url}")
    lines.append(f"Timestamp: {results['timestamp']}")
    lines.append(f"HTTP status: {results['http_status']}")
    lines.append("")

    lines.append(f"Visited unique domains: {len(results['visited_domains'])}")
    for d in results["visited_domains"]:
        lines.append(f"  - {d}")
    lines.append("")

    lines.append(f"Redirect chain length: {len(results['redirect_chain'])}")
    for u in results["redirect_chain"]:
        lines.append(f"  -> {u}")
    lines.append("")

    lines.append("Console messages:")
    if results["console_messages"]:
        for m in results["console_messages"]:
            lines.append(f"  - {m}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append(f"Automatic download detected: {results['auto_download']}")
    lines.append("")




    #scoring    
    score = 0

    redirect_count = len(results["redirect_chain"])
    if redirect_count > 5:
        score += 5
    elif redirect_count > 10:
        score += 10

    popup_count = len(results["popup_urls"])
    if popup_count > 0:
        score += popup_count * 20

    if results["auto_download"]:
        score += 40

    domain_count = len(results["visited_domains"])
    if domain_count > 25:
        score += 10

    console_errors = sum(1 for msg in results["console_messages"] if msg.startswith("error"))
    if console_errors > 10:
        score += 5

    if score < 20:
        verdict = "SAFE"
    elif score < 50:
        verdict = "SUSPICIOUS"
    else:
        verdict = "MALICIOUS"

    if results["http_status"] is None and "ERR_" in " ".join(results["console_messages"]):
        verdict = "UNKNOWN (Page failed to load - SSL error?)"
        score = 999  # special error score



    
    lines.append(f"Simple verdict: {verdict} (score {score})")




    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Analysis complete. Files written:", OUT_TXT)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_url.py <url>")
        sys.exit(1)

    analyze(sys.argv[1])
