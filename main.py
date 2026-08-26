# 🎯 Project: Web Directory Scanner
#
# What it does:
# Takes an authorized target URL and a wordlist, requests each path,
# and reports potentially interesting responses.
#
# ⚠️ Ethical Use Only:
# Use this only on systems you own or have explicit permission to test.


import argparse
import time
from pathlib import Path
from urllib.parse import urlparse

import requests


# -----------------------------
# ARGUMENTS
# -----------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Web directory scanner for authorized testing"
    )

    parser.add_argument(
        "target",
        help="Target URL, e.g. https://example.com"
    )

    parser.add_argument(
        "wordlist",
        help="Path to the wordlist file"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Save discovered results to a file"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0,
        help="Delay between requests in seconds"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5,
        help="Request timeout in seconds"
    )

    return parser.parse_args()


# -----------------------------
# VALIDATION
# -----------------------------

def validate_arguments(args):

    target = args.target.strip().rstrip("/")

    parsed = urlparse(target)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            "Target must start with http:// or https://"
        )

    if not parsed.netloc:
        raise ValueError("Invalid target URL.")

    if args.delay < 0:
        raise ValueError("Delay cannot be negative.")

    if args.timeout <= 0:
        raise ValueError("Timeout must be greater than 0.")

    return target


# -----------------------------
# LOAD WORDLIST
# -----------------------------

def load_wordlist(filename):

    try:
        with open(filename, "r", encoding="utf-8") as file:

            paths = [
                line.strip()
                for line in file
                if line.strip()
            ]

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Wordlist not found: {filename}"
        )

    except OSError as error:
        raise OSError(
            f"Could not read wordlist: {error}"
        )

    # Remove duplicates while keeping original order
    paths = list(dict.fromkeys(paths))

    if not paths:
        raise ValueError("Wordlist is empty.")

    return paths


# -----------------------------
# SAVE RESULT
# -----------------------------

def save_result(text, output_file):

    if not output_file:
        return

    try:
        with open(output_file, "a", encoding="utf-8") as file:
            file.write(text + "\n")

    except OSError as error:
        print(f"[-] Could not write result: {error}")


# -----------------------------
# HTTP REQUEST
# -----------------------------

def make_request(session, url, timeout):

    try:
        return session.get(
            url,
            timeout=timeout,
            allow_redirects=False
        )

    except requests.RequestException:
        return None


# -----------------------------
# BASELINE
# -----------------------------

def get_baseline(session, target, timeout):

    test_url = (
        f"{target}/"
        "this-should-not-exist-123456"
    )

    response = make_request(
        session,
        test_url,
        timeout
    )

    if response is None:
        raise ConnectionError(
            "Could not establish baseline response."
        )

    return response.status_code, len(response.content)


# -----------------------------
# FORMAT RESULT
# -----------------------------

def classify_response(
    response,
    url,
    baseline_length
):

    status = response.status_code
    size = len(response.content)

    # 200
    if status == 200:

        if size != baseline_length:
            return (
                f"[+] 200 - {url} - "
                f"Size: {size}"
            )

        return None

    # 403
    if status == 403:
        return f"[!] 403 - {url}"

    # 301 / 302
    if status in (301, 302):

        location = response.headers.get(
            "Location",
            "Unknown"
        )

        return (
            f"[>] {status} - "
            f"{url} -> {location}"
        )

    return None


# -----------------------------
# SCANNER
# -----------------------------

def scan(
    target,
    paths,
    output_file,
    delay,
    timeout
):

    session = requests.Session()

    print(f"\n[+] Target: {target}")
    print(f"[+] Wordlist entries: {len(paths)}")

    if output_file:
        print(f"[+] Output: {output_file}")

    if delay > 0:
        print(f"[+] Delay: {delay} seconds")

    print(f"[+] Timeout: {timeout} seconds")

    # Baseline
    try:
        baseline_status, baseline_length = get_baseline(
            session,
            target,
            timeout
        )

    except ConnectionError as error:
        print(f"[-] {error}")
        return

    print(f"[+] Baseline status: {baseline_status}")
    print(f"[+] Baseline size: {baseline_length}")

    print("\n[+] Starting scan...\n")

    total = len(paths)

    for number, path in enumerate(paths, start=1):

        url = f"{target}/{path.lstrip('/')}"

        print(
            f"[{number}/{total}] "
            f"Checking {url}"
        )

        response = make_request(
            session,
            url,
            timeout
        )

        if response is None:
            print(f"[-] Request failed: {url}")

        else:
            result = classify_response(
                response,
                url,
                baseline_length
            )

            if result:
                print(result)
                save_result(
                    result,
                    output_file
                )

        if delay > 0:
            time.sleep(delay)

    print("\n[+] Scan complete.")


# -----------------------------
# MAIN
# -----------------------------

def main():

    args = parse_arguments()

    try:
        target = validate_arguments(args)

        paths = load_wordlist(
            args.wordlist
        )

        scan(
            target=target,
            paths=paths,
            output_file=args.output,
            delay=args.delay,
            timeout=args.timeout
        )

    except (
        ValueError,
        FileNotFoundError,
        OSError
    ) as error:

        print(f"[-] {error}")


if __name__ == "__main__":
    main()