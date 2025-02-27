import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from urllib.parse import urlparse

# CSV file paths
INPUT_CSV = "CC-MAIN-2025-08"  # CSV file with websites
OUTPUT_CSV = "CC-MAIN-2025-08_FINAL.csv"

# Helper function to normalize URLs by ensuring they have a scheme
def normalize_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        # Prepend "https://" if no scheme is present
        url = "https://" + url
    return url

# Function to check if a website supports both Japanese and Korean
def check_bilingual_language(url):
    # Normalize the URL
    url = normalize_url(url)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Get the lang attribute from the <html> tag (if available)
        html_tag = soup.find("html")
        html_lang = html_tag.get("lang", "").lower() if html_tag else ""
        
        # Get all alternate hreflang links (e.g., <link rel="alternate" hreflang="ja" ...>)
        hreflang_links = soup.find_all("link", attrs={"rel": "alternate", "hreflang": True})
        hreflangs = {link["hreflang"].lower() for link in hreflang_links if link.get("hreflang")}
        
        # Check if both 'ja' and 'ko' are present
        if "ja" in hreflangs and "ko" in hreflangs:
            return True, html_lang, ", ".join(hreflangs)
        
    except Exception as e:
        print(f"Error checking {url}: {e}")
    
    return False, "", ""

# Function to extract the domain from a URL
def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Function to load websites from CSV and check each one for bilingual support
def check_websites_from_csv(input_csv, num_websites=30000):
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading CSV file {input_csv}: {e}")
        return

    # Attempt to get the website column (change column name if needed)
    if "Website" in df.columns:
        websites = df["Website"].dropna().unique()
    elif "URL" in df.columns:
        websites = df["URL"].dropna().unique()
    else:
        print("CSV file must contain a 'Website' or 'URL' column.")
        return

    websites_checked = set()
    bilingual_sites = []

    for website in websites:
        if len(bilingual_sites) >= num_websites:
            break

        # Normalize and extract domain name to avoid duplicates
        website = normalize_url(website)
        domain = extract_domain(website)
        if domain in websites_checked:
            continue
        websites_checked.add(domain)

        print(f"Checking: {website}")
        is_bilingual, html_lang, hreflangs = check_bilingual_language(website)
        if is_bilingual:
            bilingual_sites.append((website, html_lang, hreflangs))
            print(f"✔ Found bilingual site: {website}")
        time.sleep(1)  # Delay to prevent rate limiting

    # Save results to CSV
    result_df = pd.DataFrame(bilingual_sites, columns=["Website", "HTML Lang", "Hreflangs"])
    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\n✅ Results saved to {OUTPUT_CSV}")

# Run the script using the downloaded CSV file
check_websites_from_csv(INPUT_CSV, num_websites=30000)
