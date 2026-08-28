# Import necessary libraries
import requests
from bs4 import BeautifulSoup


# ==================================================
# Getting the target site
# ==================================================

target = input(
    "Enter the Target Site/URL (format: https://example.com): "
).strip()


# ==================================================
# Paths to check
# ==================================================

path = [
    "wp-admin",
    "wp-login.php",
    "administrator",
    "user/login",
    "test",
    "php",
    "robots.txt"
]


# ==================================================
# CMS fingerprint database
# ==================================================

fingerprints = {

    "wordpress": {

        # CMS-specific paths
        "paths": {
            "wp-admin": 15,
            "wp-login.php": 20
        },

        # Status codes that may indicate
        # the endpoint exists or is handled
        "path_statuses": [
            200,
            301,
            302,
            403
        ],

        # Generator signature
        "generator": {
            "value": "WordPress",
            "score": 50
        },

        # Header signatures
        "headers": {
            "X-WP-": 25
        },

        # Content / asset signatures
        "patterns": {
            "/wp-content/": 20,
            "/wp-includes/": 20
        }
    },


    "joomla": {

        # CMS-specific paths
        "paths": {
            "administrator": 20
        },

        # Allowed status codes
        "path_statuses": [
            200,
            301,
            302,
            403
        ],

        # Generator signature
        "generator": {
            "value": "Joomla",
            "score": 50
        },

        # Header signatures
        "headers": {},

        # Content / asset signatures
        "patterns": {
            "/media/system/": 20,
            "/components/com_": 20
        }
    },


    "drupal": {

        # CMS-specific paths
        "paths": {
            "user/login": 20
        },

        # Allowed status codes
        "path_statuses": [
            200,
            301,
            302,
            403
        ],

        # Generator signature
        "generator": {
            "value": "Drupal",
            "score": 50
        },

        # Header signatures
        "headers": {},

        # Content / asset signatures
        "patterns": {
            "/sites/default/": 20,
            "/core/": 20
        }
    }
}


# ==================================================
# Store scores
# ==================================================

scores = {}


# ==================================================
# Store matched evidence
# ==================================================

matches = {}


# ==================================================
# Store signatures already counted
# ==================================================

counted_signatures = {}


# ==================================================
# Scan each path
# ==================================================

for each_path in path:

    # --------------------------------------------------
    # Build target URL
    # --------------------------------------------------

    url = f"{target.rstrip('/')}/{each_path}"


    # --------------------------------------------------
    # Send request
    # --------------------------------------------------

    response = requests.get(url)


    print("\n" + "=" * 60)

    print(
        "URL:",
        url
    )

    print(
        "Status:",
        response.status_code
    )

    print(
        "Final URL:",
        response.url
    )


    # ==================================================
    # Collect response headers
    # ==================================================

    print("\nHeaders:")

    for header_name, header_value in response.headers.items():

        print(
            f"  {header_name}: {header_value}"
        )


    # ==================================================
    # Default evidence values
    # ==================================================

    robots_content = None
    generator_value = None
    title_value = None
    script_urls = []
    link_urls = []
    canonical_value = None


    # ==================================================
    # robots.txt handling
    # ==================================================

    if each_path == "robots.txt":

        robots_content = response.text

        print("\nRobots.txt:")
        print(robots_content)


    # ==================================================
    # HTML handling
    # ==================================================

    else:

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # --------------------------------------------------
        # Generator
        # --------------------------------------------------

        generator = soup.find(
            "meta",
            attrs={
                "name": "generator"
            }
        )


        if generator:

            generator_value = generator.get(
                "content"
            )

            print(
                "\nGenerator:",
                generator_value
            )

        else:

            print(
                "\nGenerator: Not found"
            )


        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        title = soup.find("title")


        if title:

            title_value = title.get_text(
                strip=True
            )

            print(
                "Title:",
                title_value
            )

        else:

            print(
                "Title: Not found"
            )


        # --------------------------------------------------
        # JavaScript files
        # --------------------------------------------------

        scripts = soup.find_all(
            "script",
            src=True
        )


        print("\nJavaScript files:")


        for script in scripts:

            script_url = script.get(
                "src"
            )


            if script_url:

                script_urls.append(
                    script_url
                )

                print(
                    "  ",
                    script_url
                )


        # --------------------------------------------------
        # Links / CSS
        # --------------------------------------------------

        stylesheets = soup.find_all(
            "link",
            href=True
        )


        print("\nLinks / CSS:")


        for stylesheet in stylesheets:

            link_url = stylesheet.get(
                "href"
            )


            if link_url:

                link_urls.append(
                    link_url
                )

                print(
                    "  ",
                    link_url
                )


        # --------------------------------------------------
        # Canonical
        # --------------------------------------------------

        canonical = soup.find(
            "link",
            rel="canonical"
        )


        if canonical:

            canonical_value = canonical.get(
                "href"
            )

            print(
                "Canonical:",
                canonical_value
            )

        else:

            print(
                "Canonical: Not found"
            )


    # ==================================================
    # Store collected evidence
    # ==================================================

    evidence = {

        "url": url,

        "status": response.status_code,

        "final_url": response.url,

        "headers": dict(
            response.headers
        ),

        "generator": generator_value,

        "title": title_value,

        "scripts": script_urls,

        "links": link_urls,

        "canonical": canonical_value,

        "robots": robots_content
    }


    # ==================================================
    # Fingerprint matching
    # ==================================================

    print("\nFingerprint Matches:")


    for cms_name, fingerprint in fingerprints.items():

        # --------------------------------------------------
        # Initialize CMS storage
        # --------------------------------------------------

        if cms_name not in scores:

            scores[cms_name] = 0


        if cms_name not in matches:

            matches[cms_name] = []


        if cms_name not in counted_signatures:

            counted_signatures[cms_name] = set()


        # ==================================================
        # 1. Path matching
        # ==================================================

        path_signatures = fingerprint.get(
            "paths",
            {}
        )


        path_statuses = fingerprint.get(
            "path_statuses",
            []
        )


        if each_path in path_signatures:

            if response.status_code in path_statuses:

                path_score = path_signatures[
                    each_path
                ]


                signature_key = (
                    "path:"
                    + each_path.lower()
                )


                if (
                    signature_key
                    not in counted_signatures[cms_name]
                ):

                    scores[cms_name] += path_score

                    counted_signatures[
                        cms_name
                    ].add(
                        signature_key
                    )


                    matches[cms_name].append({

                        "type": "path",

                        "value": each_path,

                        "status": response.status_code,

                        "score": path_score
                    })


                    print(
                        f"  [MATCH] {cms_name} "
                        f"→ path: /{each_path} "
                        f"[{response.status_code}] "
                        f"(+{path_score})"
                    )


        # ==================================================
        # 2. Generator matching
        # ==================================================

        generator_signature = fingerprint.get(
            "generator"
        )


        if (
            generator_signature
            and evidence["generator"]
            and generator_signature["value"].lower()
            in evidence["generator"].lower()
        ):

            signature_key = (
                "generator:"
                + generator_signature["value"].lower()
            )


            if (
                signature_key
                not in counted_signatures[cms_name]
            ):

                score_value = generator_signature[
                    "score"
                ]


                scores[cms_name] += score_value


                counted_signatures[
                    cms_name
                ].add(
                    signature_key
                )


                matches[cms_name].append({

                    "type": "generator",

                    "value": evidence["generator"],

                    "score": score_value
                })


                print(
                    f"  [MATCH] {cms_name} "
                    f"→ generator: "
                    f"{evidence['generator']} "
                    f"(+{score_value})"
                )


        # ==================================================
        # 3. Header matching
        # ==================================================

        headers = fingerprint.get(
            "headers",
            {}
        )


        for header_signature, header_score in headers.items():

            header_signature_lower = (
                header_signature.lower()
            )


            header_matched = False


            for response_header in evidence["headers"]:

                response_header_lower = (
                    response_header.lower()
                )


                if (
                    header_signature_lower
                    in response_header_lower
                ):

                    signature_key = (
                        "header:"
                        + header_signature_lower
                    )


                    if (
                        signature_key
                        not in counted_signatures[cms_name]
                    ):

                        scores[cms_name] += header_score


                        counted_signatures[
                            cms_name
                        ].add(
                            signature_key
                        )


                        matches[cms_name].append({

                            "type": "header",

                            "value": response_header,

                            "score": header_score
                        })


                        print(
                            f"  [MATCH] {cms_name} "
                            f"→ header: "
                            f"{response_header} "
                            f"(+{header_score})"
                        )


                    header_matched = True

                    break


        # ==================================================
        # 4. Pattern matching
        # ==================================================

        patterns = fingerprint.get(
            "patterns",
            {}
        )


        for pattern, pattern_score in patterns.items():

            pattern_lower = pattern.lower()


            signature_key = (
                "pattern:"
                + pattern_lower
            )


            pattern_matched = False

            pattern_source = None


            # --------------------------------------------------
            # Check JavaScript URLs
            # --------------------------------------------------

            for script_url in evidence["scripts"]:

                if pattern_lower in script_url.lower():

                    pattern_matched = True
                    pattern_source = "script"

                    break


            # --------------------------------------------------
            # Check CSS / links
            # --------------------------------------------------

            if not pattern_matched:

                for link_url in evidence["links"]:

                    if pattern_lower in link_url.lower():

                        pattern_matched = True
                        pattern_source = "link"

                        break


            # --------------------------------------------------
            # Check robots.txt
            # --------------------------------------------------

            if (
                not pattern_matched
                and evidence["robots"]
            ):

                if pattern_lower in evidence["robots"].lower():

                    pattern_matched = True
                    pattern_source = "robots"


            # --------------------------------------------------
            # Add score once
            # --------------------------------------------------

            if (
                pattern_matched
                and signature_key
                not in counted_signatures[cms_name]
            ):

                scores[cms_name] += pattern_score


                counted_signatures[
                    cms_name
                ].add(
                    signature_key
                )


                matches[cms_name].append({

                    "type": "pattern",

                    "value": pattern,

                    "source": pattern_source,

                    "score": pattern_score
                })


                print(
                    f"  [MATCH] {cms_name} "
                    f"→ pattern: {pattern} "
                    f"[{pattern_source}] "
                    f"(+{pattern_score})"
                )


# ==================================================
# Final CMS selection + Confidence
# ==================================================

if scores:

    # Sort CMSs from highest score to lowest score
    ranked_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Best candidate
    detected_cms = ranked_scores[0][0]
    detected_score = ranked_scores[0][1]

    # Runner-up candidate
    if len(ranked_scores) > 1:
        runner_up_cms = ranked_scores[1][0]
        runner_up_score = ranked_scores[1][1]
    else:
        runner_up_cms = None
        runner_up_score = 0

    # Calculate score gap
    score_gap = detected_score - runner_up_score

    # --------------------------------------------------
    # Check for tie
    # --------------------------------------------------

    if detected_score == 0:

        confidence = "Unknown"
        detected_cms = "Unknown"

    elif detected_score == runner_up_score:

        confidence = "Low"
        detected_cms = "Ambiguous"

    elif detected_score >= 70 and score_gap >= 30:

        confidence = "High"

    elif detected_score >= 40 and score_gap >= 15:

        confidence = "Medium"

    elif detected_score >= 20:

        confidence = "Low"

    else:

        confidence = "Unknown"


    # --------------------------------------------------
    # Final output
    # --------------------------------------------------

    print("\n" + "=" * 60)

    print("FINAL RESULT")

    print(
        "CMS:",
        detected_cms
    )

    print(
        "Score:",
        detected_score
    )

    print(
        "Confidence:",
        confidence
    )

    if runner_up_cms:

        print(
            "Runner-up:",
            runner_up_cms
        )

        print(
            "Runner-up Score:",
            runner_up_score
        )

        print(
            "Score Gap:",
            score_gap
        )


else:

    print("\nNo CMS evidence found.")