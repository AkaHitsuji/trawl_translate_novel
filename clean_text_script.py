import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

def replace_and_clean_lines(folder_path, target_string, limit=200):
    matches = []
    replacements_by_file = {}

    # Step 1: Find up to `limit` matches
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if target_string in line:
                    matches.append((filename, i, line))
                    replacements_by_file.setdefault(filename, []).append(i)
                    if len(matches) >= limit:
                        break
        if len(matches) >= limit:
            break

    # Step 2: Show matches
    if not matches:
        logger.info(f"No occurrences of '{target_string}' found.")
        return

    logger.info(f"\nFound the first {len(matches)} occurrences of '{target_string}':\n")
    for filename, lineno, line in matches:
        logger.info(f"{filename} (Line {lineno + 1}): {line.strip()}")

    # Step 3: Ask for confirmation
    confirm = input(f"\nDo you want to replace and delete lines that become empty? (yes/no): ").strip().lower()
    if confirm != 'yes':
        logger.info("Aborted.")
        return

    # Step 4: Replace + remove lines that become empty
    for filename, line_indices in replacements_by_file.items():
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated_lines = []
        for i, line in enumerate(lines):
            if i in line_indices:
                modified = line.replace(target_string, '')
                if modified.strip():  # keep non-empty lines
                    updated_lines.append(modified.strip() + '\n')
            else:
                updated_lines.append(line.strip() + '\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

    logger.info(f"\nProcessed {len(matches)} matches: replaced and removed any lines left empty.")

# Example usage
if __name__ == "__main__":
    folder = input("Enter the folder path: ").strip()
    text_to_remove = input("Enter the text to remove (delete line if empty after): ").strip()
    replace_and_clean_lines(folder, text_to_remove)