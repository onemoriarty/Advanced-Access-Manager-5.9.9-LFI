# Advanced-Access-Manager-5.9.9-LFI

## WordPress Advanced Access Manager \< 5.9.9 - Local File Inclusion (LFI) Scanner

This tool is a Python-based scanner designed to detect and exploit a critical Local File Inclusion (LFI) vulnerability found in versions prior to 5.9.9 of the popular **Advanced Access Manager** plugin used in WordPress sites.

### Purpose

The primary objective of this scanner is to assist security researchers and penetration testers in quickly and effectively identifying the LFI vulnerability in WordPress installations running vulnerable versions of the Advanced Access Manager plugin. When the vulnerability is detected, the tool also attempts to retrieve the content of sensitive files like `wp-config.php`, demonstrating the severity of the vulnerability and potentially exposing database credentials.

### Vulnerability Details

  * **Plugin Name:** Advanced Access Manager

  * **Affected Versions:** All versions prior to 5.9.9 (`< 5.9.9`)

  * **Vulnerability Type:** Local File Inclusion (LFI)

  * **Exploitation Parameter:** `aam-media` (Example: `http://target.com/?aam-media=../../../../etc/passwd`)

  * **CWE:** CWE-22 (Path Traversal)

  * **CVSS Score:** 9.1 (Critical) according to WPScan

  * **CVE ID:** As of now, there is no known CVE number specifically assigned to this particular LFI vulnerability. However, this does not diminish the critical nature and potential impact of the vulnerability.

This vulnerability allows attackers to access arbitrary files on the server. Specifically, reading files like `wp-config.php` can lead to the compromise of database credentials and ultimately, a complete takeover of the site.

### Installation

To use this tool, you need Python 3 and the `requests` library.

1.  **Python 3 Installation:** Ensure Python 3 is installed on your system.

2.  **Install Required Libraries:**

    ```
    pip install requests
    ```

### Usage

You can run the tool from the command line. It supports scanning a single URL or providing a list of URLs.

To see the available options and help message:

```
python exp.py
```

**Usage Options:**

  * `-u`, `--url`: Single target URL (e.g., `http://example.com`)

  * `-l`, `--list`: File containing target URLs (one URL per line)

  * `-w`, `--workers`: Number of concurrent workers (threads) to run (default: 50)

**File Fetching Options:**

The tool attempts to fetch `wp-config.php` to confirm the vulnerability. If the vulnerability is found, you will be prompted whether you want the tool to fetch other sensitive files (e.g., `debug.log`, `version.php`, `README.txt`, `.env`).

  * To fetch all sensitive documents: Type `all`

  * To fetch specific files: Enter the numbers of the files separated by commas (e.g., `1,3`)

  * If you don't want to fetch anything: Leave it blank and press Enter.

**Example Usages:**

1.  **Scan a single URL and fetch all sensitive files:**

    ```
    python exp.py -u http://example.com
    ```

    (Type `all` when prompted)

2.  **Scan a list of URLs (with default workers) and only fetch `wp-config.php` (no other files):**

    ```
    python exp.py -l urls.txt
    ```

    (Press Enter without typing anything when prompted)

3.  **Scan a list of URLs with more workers and fetch specific files:**

    ```
    python exp.py -l targets.txt -w 100
    ```

    (Type `2,4` when prompted)

### Important Notes and Warnings

  * **Legal and Ethical Use:** This tool is intended for educational purposes only and should be used exclusively on systems for which you have explicit legal authorization. Using this tool without prior consent on target systems is illegal and may lead to severe consequences.

  * **Disclaimer:** The developer is not responsible for any misuse of this tool. The user is solely responsible for complying with all applicable local, national, and international laws before using the tool.

  * **Stay Updated:** Vulnerabilities are continuously discovered and patched. This tool targets a specific vulnerability. The best security practice is always to keep your software and plugins updated to their latest versions.

  * **Performance:** A large number of URLs or a high worker count can impose a significant load on target servers. Please use responsibly.

### Developer Information

  * **Author:** onemoriarty

  * **Discord:** [https://discord.gg/QRppCpjvZc](https://discord.gg/QRppCpjvZc)

  * **Forum:** [warnight.rf.gd](https://www.google.com/search?q=http://warnight.rf.gd)

### License

This project is open-source, and no specific license is explicitly stated. However, adherence to legal and ethical usage principles is strongly advised.
