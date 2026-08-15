import requests
import re
import json


# ==========================================
# 1. GET TARGET
# ==========================================

target = input("Enter your domain: ").strip().lower()


# ==========================================
# 2. CLEAN DOMAIN
# ==========================================

def clean_domain(name):

    name = name.strip().lower()

    # Remove protocol
    name = re.sub(r"^https?://", "", name)

    # Remove wildcard
    name = name.removeprefix("*.")

    # Remove path
    name = name.split("/")[0]

    # Remove port
    name = name.split(":")[0]

    # Remove trailing dot
    name = name.rstrip(".")

    return name


# ==========================================
# 3. CHECK SCOPE
# ==========================================

def in_scope(name):

    return (
        name == target
        or name.endswith("." + target)
    )


# ==========================================
# 4. URLSCAN
# ==========================================

def urlscan():

    print("\n[+] Searching URLScan...")

    found = set()

    url = "https://urlscan.io/api/v1/search/"

    params = {
        "q": f"domain:{target}"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        if response.status_code != 200:

            print(
                "[-] URLScan failed:",
                response.status_code
            )

            return found

        data = response.json()

        for result in data.get("results", []):

            page = result.get("page", {})

            domain = page.get("domain")

            if domain:

                domain = clean_domain(domain)

                if in_scope(domain):

                    found.add(domain)

        print(
            f"[+] URLScan found "
            f"{len(found)} domains"
        )

    except requests.RequestException as error:

        print("[-] URLScan error:", error)

    except ValueError:

        print("[-] URLScan returned invalid JSON")

    return found


# ==========================================
# 5. WAYBACK MACHINE
# ==========================================

def wayback():

    print("\n[+] Searching Wayback Machine...")

    found = set()

    url = "https://web.archive.org/cdx/search/cdx"

    params = {

        "url": f"*.{target}/*",

        "output": "json",

        "fl": "original",

        "collapse": "urlkey"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        if response.status_code != 200:

            print(
                "[-] Wayback failed:",
                response.status_code
            )

            return found

        data = response.json()

        for row in data:

            if not row:
                continue

            original_url = row[0]

            match = re.search(
                r"https?://([^/:]+)",
                original_url
            )

            if match:

                hostname = clean_domain(
                    match.group(1)
                )

                if in_scope(hostname):

                    found.add(hostname)

        print(
            f"[+] Wayback found "
            f"{len(found)} domains"
        )

    except requests.RequestException as error:

        print("[-] Wayback error:", error)

    except ValueError:

        print(
            "[-] Wayback returned "
            "invalid JSON"
        )

    return found


# ==========================================
# 6. RAPIDDNS
# ==========================================

def rapiddns():

    print("\n[+] Searching RapidDNS...")

    found = set()

    url = (
        f"https://rapiddns.io/subdomain/"
        f"{target}?full=1"
    )

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code != 200:

            print(
                "[-] RapidDNS failed:",
                response.status_code
            )

            return found

        pattern = (
            r"[a-zA-Z0-9*._-]+\."
            + re.escape(target)
        )

        matches = re.findall(
            pattern,
            response.text
        )

        for hostname in matches:

            hostname = clean_domain(hostname)

            if in_scope(hostname):

                found.add(hostname)

        print(
            f"[+] RapidDNS found "
            f"{len(found)} domains"
        )

    except requests.RequestException as error:

        print("[-] RapidDNS error:", error)

    return found


# ==========================================
# 7. CERTSPOTTER
# ==========================================

def certspotter():

    print("\n[+] Searching CertSpotter...")

    found = set()

    url = (
        "https://api.certspotter.com/"
        "v1/issuances"
    )

    params = {

        "domain": target,

        "include_subdomains": "true",

        "expand": "dns_names"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        if response.status_code != 200:

            print(
                "[-] CertSpotter failed:",
                response.status_code
            )

            return found

        data = response.json()

        for record in data:

            for name in record.get(
                "dns_names",
                []
            ):

                name = clean_domain(name)

                if in_scope(name):

                    found.add(name)

        print(
            f"[+] CertSpotter found "
            f"{len(found)} domains"
        )

    except requests.RequestException as error:

        print("[-] CertSpotter error:", error)

    except ValueError:

        print(
            "[-] CertSpotter returned "
            "invalid JSON"
        )

    return found


# ==========================================
# 8. COMMON CRAWL
# ==========================================

def commoncrawl():

    print("\n[+] Searching Common Crawl...")

    found = set()

    index_url = (
        "https://index.commoncrawl.org/"
        "collinfo.json"
    )

    try:

        response = requests.get(
            index_url,
            timeout=20
        )

        if response.status_code != 200:

            print(
                "[-] Common Crawl index failed:",
                response.status_code
            )

            return found

        indexes = response.json()

        if not indexes:

            print(
                "[-] No Common Crawl "
                "indexes found"
            )

            return found

        latest_index = indexes[0]["cdx-api"]

        params = {

            "url": f"*.{target}/*",

            "output": "json",

            "filter": "status:200",

            "collapse": "urlkey"
        }

        response = requests.get(
            latest_index,
            params=params,
            timeout=30
        )

        if response.status_code != 200:

            print(
                "[-] Common Crawl query failed:",
                response.status_code
            )

            return found

        for line in response.text.splitlines():

            try:

                record = json.loads(line)

                original_url = record.get("url")

                if not original_url:
                    continue

                match = re.search(
                    r"https?://([^/:]+)",
                    original_url
                )

                if match:

                    hostname = clean_domain(
                        match.group(1)
                    )

                    if in_scope(hostname):

                        found.add(hostname)

            except json.JSONDecodeError:

                continue

        print(
            f"[+] Common Crawl found "
            f"{len(found)} domains"
        )

    except requests.RequestException as error:

        print("[-] Common Crawl error:", error)

    except ValueError:

        print(
            "[-] Common Crawl returned "
            "invalid JSON"
        )

    return found


# ==========================================
# 9. ANUBISDB
# ==========================================

def anubisdb():

    print("\n[+] Searching AnubisDB...")

    found = set()

    url = (
        f"https://jldc.me/anubis/subdomains/"
        f"{target}"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:

            print(
                "[-] AnubisDB failed:",
                response.status_code
            )

            return found

        data = response.json()

        if isinstance(data, list):

            for name in data:

                name = clean_domain(name)

                if in_scope(name):

                    found.add(name)

        print(
            f"[+] AnubisDB found "
            f"{len(found)} domains"
        )

    except requests.RequestException as error:

        print("[-] AnubisDB error:", error)

    except ValueError:

        print(
            "[-] AnubisDB returned "
            "invalid JSON"
        )

    return found


# ==========================================
# 10. RUN SOURCES
# ==========================================

sources = [

    urlscan,

    wayback,

    rapiddns,

    certspotter,

    commoncrawl,

    anubisdb
]


# ==========================================
# 11. COMBINE RESULTS
# ==========================================

all_subdomains = set()


for source in sources:

    try:

        results = source()

        all_subdomains.update(results)

    except Exception as error:

        print(
            f"[-] Source error: {error}"
        )


# ==========================================
# 12. FINAL RESULTS
# ==========================================

print("\n" + "=" * 50)

print("FINAL RESULTS")

print("=" * 50)

print(
    f"\nTotal unique domains: "
    f"{len(all_subdomains)}\n"
)


for subdomain in sorted(all_subdomains):

    print(subdomain)


# ==========================================
# 13. SAVE RESULTS
# ==========================================

with open(
    "subdomains.txt",
    "w"
) as file:

    for subdomain in sorted(all_subdomains):

        file.write(
            subdomain + "\n"
        )


print(
    "\n[+] Results saved to "
    "subdomains.txt"
)