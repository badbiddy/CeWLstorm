import argparse
import requests
import threading
import json
import os
import time
import pdfplumber
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

visited_urls = set()
wordlist = set()

common_ignore_words = {
    "the", "and", "for", "with", "from", "about", "this", "that", "you",
    "your", "our", "their", "have", "has", "will", "was", "were", "can",
    "not", "are", "but", "should", "would", "which", "who", "what", "where"
}

def fetch_with_selenium(url, user_agent, proxy):
    """Fetch JavaScript-rendered content using Selenium, ensuring full load."""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid headless detection
    options.add_argument("--headless=new")  # New headless mode
    options.add_argument(f"user-agent={user_agent}")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # Bypass detection

    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Ensure full content loads
    time.sleep(2)

    html = driver.page_source
    print(f"[DEBUG] Selenium fetched {len(html)} bytes from {url}")
    print(f"[DEBUG] First 500 characters of JS-rendered page:\n{html[:500]}")

    driver.quit()
    return html

def extract_words(html, min_length):
    """Extract only meaningful, visible words and generate variations."""
    soup = BeautifulSoup(html, "html.parser")

    text = " ".join([
        t.strip() for t in soup.find_all(string=True)
        if t.parent.name not in ["script", "style", "noscript", "meta", "link", "head", "title"]
        and len(t.strip()) > 0
    ])

    print(f"[DEBUG] Extracted raw text (first 500 chars): {text[:500]}")

    words = set(filter(lambda w: len(w) >= min_length and w.isalpha() and w.lower() not in common_ignore_words, text.split()))

    # Store original, uppercase, and lowercase versions
    for word in words:
        wordlist.add(word)  # Original format
        wordlist.add(word.upper())  # Uppercase variation
        wordlist.add(word.lower())  # Lowercase variation

    print(f"[DEBUG] Extracted words (including variations): {len(wordlist)} found")
    if wordlist:
        print(f"[DEBUG] Sample words: {list(wordlist)[:10]}")

def load_wifi_names(file_path):
    """Load Wi-Fi names from a user-specified file."""
    wifi_names = []
    if file_path and os.path.isfile(file_path):
        with open(file_path, "r") as f:
            wifi_names = [line.strip() for line in f.readlines()]
    return wifi_names

def append_wifi_mutations(wifi_names):
    """Prepend and append Wi-Fi names to extracted words."""
    if not wifi_names:
        return

    wifi_mutations = set()

    for wifi in wifi_names:
        wifi = wifi.lower()  # Normalize Wi-Fi names to lowercase

        # Basic Wi-Fi name mutations
        wifi_mutations.update([
            wifi, wifi.upper(), wifi + "123", wifi + "2024"
        ])

        # Prepend and append Wi-Fi names to each extracted word
        for word in list(wordlist):
            wifi_mutations.add(wifi + word)  # Prepend Wi-Fi name
            wifi_mutations.add(word + wifi)  # Append Wi-Fi name

    wordlist.update(wifi_mutations)
    print(f"[INFO] Added {len(wifi_mutations)} Wi-Fi-based mutations to the wordlist")

def save_wordlist(filename):
    """Save final wordlist to a file, ensuring words are sorted and unique."""
    sorted_words = sorted(wordlist)
    with open(filename, "w") as f:
        for word in sorted_words:
            f.write(word + "\n")

    print(f"[INFO] Wordlist saved to {filename} ({len(sorted_words)} words)")

def crawl(url, depth, include_js, user_agent, proxy, min_length):
    """Recursively crawl a website."""
    if depth == 0 or url in visited_urls:
        return

    visited_urls.add(url)
    html = fetch_with_selenium(url, user_agent, proxy) if include_js else None

    if html:
        extract_words(html, min_length)

def main():
    parser = argparse.ArgumentParser(description="CeWLstorm - Custom Word List Generator for WPA2-PSK & Pentesting")

    parser.add_argument("url", type=str, help="URL to start crawling from")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Recursion depth (default: 2)")
    parser.add_argument("-js", "--include-js", action="store_true", help="Include JavaScript-rendered words (requires Selenium)")
    parser.add_argument("-wl", "--wordlist", default="wordlist.txt", help="Output wordlist filename")
    parser.add_argument("--wifi-names", help="File containing Wi-Fi names to prepend/append to the wordlist")

    global args
    args = parser.parse_args()

    # Run the main crawling process
    crawl(args.url, args.depth, args.include_js, "Mozilla/5.0", None, 5)

    # Load Wi-Fi names and apply mutations before saving
    wifi_names = load_wifi_names(args.wifi_names)
    append_wifi_mutations(wifi_names)

    # Save the final wordlist
    save_wordlist(args.wordlist)

if __name__ == "__main__":
    main()
