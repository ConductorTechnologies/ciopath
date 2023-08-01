import sys

def replace_semver_parts(file_path):
    """Replace the -rc, -beta, and -alpha parts of a version string with r, b, and a, respectively."""
    replacements = {
        '-rc.': 'r',
        '-beta.': 'b',
        '-alpha.': 'a'
    }

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    for old_string, new_string in replacements.items():
        content = content.replace(old_string, new_string).strip()

    return content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the file path as a command-line argument.")
        sys.exit(1)

    replaced_content = replace_semver_parts(sys.argv[1])
    print(replaced_content)
