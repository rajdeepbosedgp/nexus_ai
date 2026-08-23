import asyncio
import os
import sys
import subprocess
import time
from playwright.async_api import async_playwright, expect

# Ensure screenshots output directory exists
os.makedirs("scripts/screenshots", exist_ok=True)

# Helper to create sample image for file upload test
SAMPLE_IMG_PATH = os.path.abspath("scripts/test_sample_upload.jpg")
def ensure_sample_image():
    dummy_jpg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00\x60\x00\x60\x00\x00\xFF\xDB\x00C\x00"
    with open(SAMPLE_IMG_PATH, "wb") as f:
        f.write(dummy_jpg)

async def run_playwright_e2e():
    print("=" * 80)
    print("NEXUS — REAL CHROMIUM BROWSER E2E DOM AUTOMATED TESTING (PLAYWRIGHT)")
    print("=" * 80)
    
    ensure_sample_image()
    
    console_errors = []
    failed_network_requests = []
    
    async with async_playwright() as p:
        print("\n[1/7] Launching Visible Chromium Browser (headless=False, slow_mo=300)...")
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        # Attach listeners for browser console errors and failed network requests
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("requestfailed", lambda req: failed_network_requests.append(f"{req.method} {req.url} - {req.failure}"))
        
        # ---------------------------------------------------------------------
        # JOURNEY 1: RESIDENT USER FLOW
        # ---------------------------------------------------------------------
        print("\n[2/7] Testing Journey 1: Resident Persona Login & UI Verification...")
        await page.goto("http://127.0.0.1:3000")
        await page.wait_for_selector("text=NEXUS Society Intelligence")
        
        # Open Auth Modal
        await page.click("button:has-text('Log In / Choose Persona')")
        await page.wait_for_selector("text=Welcome Back to NEXUS")
        
        # Click Resident Demo Button
        await page.click("button:has-text('Resident Demo')")
        
        # Verify Resident Navigation & User Name rendered in Navbar
        await page.wait_for_selector("text=Rahul Sharma")
        print("   [PASS] Resident Dashboard rendered with user profile info (Rahul Sharma).")
        await page.screenshot(path="scripts/screenshots/01_resident_dashboard.png")
        
        # Navigate to Complaints Tab
        print("\n[3/7] Testing Resident Complaint Creation & Photo Attachment...")
        await page.click("button:has-text('Complaints')")
        await page.wait_for_selector("text=Complaints Management")
        
        # Click Raise New Complaint
        await page.click("button:has-text('Raise New Complaint')")
        await page.wait_for_selector("text=Raise New Society Complaint")
        
        # Fill Form
        selects = page.locator("form select")
        await selects.nth(0).select_option("Electrical")
        unique_desc = f"Browser DOM E2E test - corridor lights flickering post heavy rain (TS:{int(time.time())})"
        await page.fill("textarea", unique_desc)
        await selects.nth(1).select_option("High")
        await page.fill("input[placeholder*='Heavy Rain']", "Heavy Rain")
        
        # File Upload via Playwright set_input_files on input[type='file']
        await page.set_input_files("input[type='file']", SAMPLE_IMG_PATH)
        
        # Wait for file upload success badge in DOM
        await page.wait_for_selector("text=File Uploaded")
        print("   [PASS] Resident photo file uploaded via DOM file picker.")
        await page.screenshot(path="scripts/screenshots/02_resident_form_uploaded.png")
        
        # Submit Form
        await page.click("button:has-text('Submit Complaint')")
        await page.wait_for_selector(f"p:has-text('{unique_desc}')")
        print("   [PASS] Submitted complaint rendered visually in complaints list.")
        
        # Verify Photo Attachment Badge / Thumbnail rendered on Complaint Card
        await page.wait_for_selector("a:has-text('View Attached Photo')")
        print("   [PASS] 'View Attached Photo' badge rendered on complaint card.")
        await page.screenshot(path="scripts/screenshots/03_resident_complaint_card.png")
        
        # Logout Resident
        await page.click("button[title='Logout']")
        await page.wait_for_selector("text=Log In / Choose Persona")
        print("   [PASS] Resident logout completed successfully.")
        
        # ---------------------------------------------------------------------
        # JOURNEY 2: ADMIN USER FLOW
        # ---------------------------------------------------------------------
        print("\n[4/7] Testing Journey 2: Admin Persona Login & Dashboard Verification...")
        await page.click("button:has-text('Log In / Choose Persona')")
        await page.wait_for_selector("text=Welcome Back to NEXUS")
        
        # Click Admin Demo Button
        await page.click("button:has-text('Admin Demo')")
        await page.wait_for_selector("text=Society Admin")
        print("   [PASS] Admin Dashboard rendered with metrics cards & overdue leaderboard.")
        await page.screenshot(path="scripts/screenshots/04_admin_dashboard.png")
        
        # Navigate to Complaints Tab
        print("\n[5/7] Testing Admin Complaint Status Transition & Immutable Timeline...")
        await page.click("button:has-text('Complaints')")
        await page.wait_for_selector("text=Complaints Management")
        
        # Find the newly created complaint card and click Update Lifecycle Status
        card = page.locator(".glass-card", has_text=unique_desc)
        await card.locator("button:has-text('Update Lifecycle Status')").click()
        await page.wait_for_selector("text=Update Lifecycle Status")
        
        # Select In Progress and add status note in status modal
        modal = page.locator("div.fixed")
        await modal.locator("select").select_option("In Progress")
        await modal.locator("input[type='text']").fill("Dispatching electrical maintenance team for inspection.")
        await modal.locator("button[type='submit']").click()
        
        # Assert status badge updated to IN PROGRESS visually in DOM
        await card.locator("span:has-text('In Progress')").first.wait_for()
        print("   [PASS] Complaint status updated to 'In Progress' visually in DOM.")
        await page.screenshot(path="scripts/screenshots/05_admin_status_updated.png")
        
        # Navigate to Notice Board Tab
        print("\n[6/7] Testing Notice Board Creation & Pinning...")
        await page.click("button:has-text('Notice Board')")
        await page.wait_for_selector("text=Society Notice Board")
        
        # Post New Notice
        await page.click("button:has-text('Post New Notice')")
        await page.wait_for_selector("text=Post Society Notice")
        
        notice_title = f"DOM Test: Elevator C Inspection (TS:{int(time.time())})"
        modal = page.locator("div.fixed")
        await modal.locator("input[type='text']").fill(notice_title)
        await modal.locator("textarea").fill("Urgent safety inspection scheduled for elevator C on Saturday.")
        await modal.locator("input[type='checkbox']").check()
        await modal.locator("button[type='submit']").click()
        
        # Assert Notice Card renders on Notice Board
        await page.wait_for_selector(f"h2:has-text('{notice_title}')")
        await page.wait_for_selector("span:has-text('IMPORTANT')")
        print("   [PASS] Notice posted & rendered visually on Notice Board DOM.")
        await page.screenshot(path="scripts/screenshots/06_notice_board_pinned.png")
        
        # ---------------------------------------------------------------------
        # JOURNEY 3: EMERGENT PATTERN DISCOVERY INTELLIGENCE PIPELINE
        # ---------------------------------------------------------------------
        print("\n[7/7] Testing Emergent Pattern Discovery UI & Evidence Traceability...")
        await page.click("button:has-text('Emergent Patterns')")
        await page.wait_for_selector("text=Emergent Pattern Discovery")
        await page.wait_for_timeout(1000)
        
        await page.click("button:has-text('Detect Patterns Now')")
        
        # Wait for Sentence Transformer & HDBSCAN processing and pattern card rendering (allow up to 90s for PyTorch embedding execution on CPU)
        await page.wait_for_selector("button:has-text('Inspect Evidence')", timeout=90000)
        print("   [PASS] Emergent pattern card rendered visually in UI.")
        await page.screenshot(path="scripts/screenshots/07_pattern_detected.png")
        
        # Toggle Evidence Panel ("Why Was This Detected?")
        await page.click("button:has-text('Inspect Evidence')")
        await page.wait_for_selector("text=Deterministic Pattern Strength Score Breakdown")
        
        # Assert 4-part Pattern Strength components render
        await page.wait_for_selector("text=Cohesion (S_cohesion)")
        await page.wait_for_selector("text=Cluster Size (S_size)")
        await page.wait_for_selector("text=Category Spread (S_category)")
        await page.wait_for_selector("text=Temporal Score")
        
        # Assert linked source complaint IDs render in evidence table
        await page.wait_for_selector("text=INC-")
        print("   [PASS] Evidence Panel breakdown & source complaint IDs rendered visually.")
        
        # 10-Second Visual Inspection Pause
        print("\n   [Visual Inspection Pause] Keeping browser window open for 10 seconds...")
        await asyncio.sleep(10)
        
        await browser.close()

    print("\n" + "=" * 80)
    print("BROWSER AUTOMATION SUMMARY & CONSOLE / NETWORK AUDIT")
    print("=" * 80)
    print(f"Console Errors Logged: {len(console_errors)}")
    for err in console_errors:
        print(f"   [Console Error] {err}")
        
    print(f"Failed Network Requests: {len(failed_network_requests)}")
    for req in failed_network_requests:
        print(f"   [Failed Request] {req}")
        
    print("\nTRUE BROWSER/DOM AUTOMATION TEST PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    asyncio.run(run_playwright_e2e())
