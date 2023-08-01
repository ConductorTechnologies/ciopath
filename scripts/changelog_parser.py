import sys

def escape_control_chars(content):
    """Escape control characters for the Slack section of the circleCI payload."""
    replacements = {
        "\n": "\\n",
        "\t": "\\t"
    }

    for old_string, new_string in replacements.items():
        content = content.replace(old_string, new_string).strip()

    return content

def get_most_recent_changes(file_path):
    """Return the most recent changes from a changelog file.
    
    We escape newlines for the Slack section of the circleCI payload. 
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        current_block = []
        for line in file:
            if "Version:" in line or "Unreleased:" in line:
                if current_block:
                    return escape_control_chars("\n".join(current_block))
            current_block.append(line.strip())

    return escape_control_chars("\n".join(current_block))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the file path as a command-line argument.")
        sys.exit(1)

    RECENT_CHANGES = get_most_recent_changes(sys.argv[1])
    print(RECENT_CHANGES)