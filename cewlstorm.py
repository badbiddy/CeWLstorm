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
extracted_usernames = set()
extracted_passwords = set()
wordlist = set()

def fetch_page(url, user_agent, proxy):
    """Fetch a webpage with optional proxy."""
    headers = {"User-Agent": user_agent}
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

def fetch_with_selenium(url, user_agent, proxy):
    """Fetch JavaScript-rendered content using Selenium."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={user_agent}")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    html = driver.page_source
    driver.quit()
    return html

def extract_words(html, min_length):
    """Extract words for wordlist generation."""
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join([t.strip() for t in soup.find_all(string=True) if t.parent.name not in ["script", "style"]])
    words = set(filter(lambda w: len(w) >= min_length, text.split()))
    wordlist.update(words)

def extract_usernames(html):
    """Extract usernames from potential login areas or emails."""
    usernames = set(re.findall(r"@([a-zA-Z0-9_.-]+)", html))  
    usernames.update(re.findall(r"/users/([a-zA-Z0-9_.-]+)", html))  
    extracted_usernames.update(usernames)

def extract_passwords(html):
    """Extract common password patterns (basic heuristic)."""
    passwords = set(re.findall(r'password["\']?\s*[:=]\s*["\']?([a-zA-Z0-9@#$%^&*]+)', html, re.IGNORECASE))
    extracted_passwords.update(passwords)

def extract_words_from_pdf(url):
    """Extract words from PDFs."""
    words = set()
    try:
        response = requests.get(url, stream=True, timeout=10)
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        
        with pdfplumber.open("temp.pdf") as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    words.update(set(text.split()))
        
        os.remove("temp.pdf")
    except:
        pass

    wordlist.update(words)

def mutate_words(wifi_names):
    """Generate wordlist mutations for password cracking."""
    mutations = set()
    leet_map = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "$", "t": "7"}

    for word in list(wordlist):
        mutations.add(word[::-1])  # Reverse words
        mutations.add(word + "123")  # Append common numbers
        mutations.add(word + "2024")  # Append the current year
        mutations.add("".join(leet_map.get(c, c) for c in word))  # Leetspeak

    # Add company Wi-Fi names as base words
    for wifi in wifi_names:
        mutations.add(wifi)
        mutations.add(wifi.lower())
        mutations.add(wifi.upper())
        mutations.add(wifi + "123")
        mutations.add(wifi + "2024")
        mutations.add(wifi[::-1])  # Reverse Wi-Fi name

    wordlist.update(mutations)

def crawl(url, depth, threads, include_js, include_pdf, user_agent, proxy):
    """Recursively crawl a website using multithreading."""
    if depth == 0 or url in visited_urls:
        return

    visited_urls.add(url)
    html = fetch_with_selenium(url, user_agent, proxy) if include_js else fetch_page(url, user_agent, proxy)

    if html:
        extract_words(html, args.min_word_length)
        extract_usernames(html)
        extract_passwords(html)
        if include_pdf:
            extract_words_from_pdf(url)

    save_wordlist(args.wordlist)

def save_wordlist(filename):
    """Save final wordlist to a file."""
    with open(filename, "w") as f:
        for word in sorted(wordlist):
            f.write(word + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="CeWLstorm - Custom Word List Generator for WPA2-PSK & Pentesting",
        usage="cewlstorm.py -h | options url",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("url", help="URL to start crawling from")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Recursion depth (default: 2)")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of concurrent threads (default: 5)")
    parser.add_argument("-js", "--include-js", action="store_true", help="Include JavaScript-rendered words (requires Selenium)")
    parser.add_argument("-pdf", "--include-pdf", action="store_true", help="Extract words from PDFs")
    parser.add_argument("-wl", "--wordlist", default="wordlist.txt", help="Output wordlist filename")
    parser.add_argument("-p", "--proxy", help="Use a proxy (format: http://127.0.0.1:8080)")
    parser.add_argument("-r", "--rate", type=int, default=10, help="Requests per second (default: 10)")
    parser.add_argument("--mutate", action="store_true", help="Apply wordlist mutations")
    parser.add_argument("--wifi-names", nargs="+", help="List of company Wi-Fi network names for targeted wordlist generation")

    global args
    args = parser.parse_args()

    crawl(args.url, args.depth, args.threads, args.include_js, args.include_pdf, "Mozilla/5.0", args.proxy)

    if args.mutate:
        mutate_words(args.wifi_names or [])

if __name__ == "__main__":
    main()
