# CeWLstorm ⚡ - Custom Wordlist Generator for Pentesting

CeWLstorm is an advanced web scraper that extracts words from websites, PDFs, and JavaScript to build **highly targeted** wordlists for WPA2-PSK cracking, fuzzing, and OSINT.

## 🚀 Features
✅ **Extract words from websites (including JavaScript-rendered content)**  
✅ **Generate multiple variations (original, uppercase, lowercase)**  
✅ **Prepend & append Wi-Fi names for stronger WPA2 password lists**  
✅ **Smart filtering (removes common words like "the", "and", etc.)**  
✅ **Leetspeak mutations (`h4ck3r -> H4CK3R`)**  
✅ **Optimized for pentesting engagements**  

## Installation
```bash
git clone https://github.com/badbiddy/CeWLstorm.git
cd CeWLstorm
pip install -r requirements.txt
```

## 🎯 Usage
### 🛠 Basic Wordlist Extraction
Extract words from a website and save them to a file:
```
python3 cewlstorm.py <URL> -wl wordlist.txt
```
### 🛠 Extract JavaScript-Rendered Words
```
python3 cewlstorm.py https://example.com/ -js -wl js_wordlist.txt
```
### 🛠 Prepend & Append Wi-Fi SSIDs
To improve WPA2 password cracking, provide a file containing Wi-Fi SSIDs:
```
python3 cewlstorm.py https://example.com/ -wl wifi_wordlist.txt --wifi-names wifi_networks.txt
```
Wi-Fi names file (wifi_networks.txt example):
```
Example_Guest
Example_Corp
Example_5G
```
### 🛠 Enable Debug Logs (Verbose Mode)
For debugging purposes, enable detailed logs:
```
python3 cewlstorm.py https://example.com/ -wl debug_wordlist.txt --verbose
```

## 📌 Wordlist Variations
CeWLstorm automatically generates multiple variations of extracted words:

```
Original: Hacker
Lowercase: hacker
Uppercase: HACKER
Leetspeak: H4CK3R
Numeric Mutations: hacker2024, hacker123
Wi-Fi Prepend & Append: Example_GuestHacker, HackerExample_Corp
```

## 🤝 Contributing
Pull requests and improvements are welcome!
If you find bugs or want to suggest new features, open an issue.

## 📍 Acknowledgments & Thank You
CeWLstorm is inspired by and builds upon the incredible work of the original CeWL and CeWLeR projects. These tools laid the foundation for targeted wordlist generation, and we extend our deepest gratitude to their creators for their contributions to the security community.

- CeWL: Created by Robin Wood (digininja) - https://digi.ninja/projects/cewl.php
- CeWLeR: Created by Roy Solberg - https://github.com/roys/cewler

Thank you for your pioneering work in custom wordlist generation, which inspired the development of CeWLstorm. 
