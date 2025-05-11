#!/usr/bin/env python
import os
import re


def fix_file(file_path):
    print(f"Fixing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix unused imports
    if file_path == 'src/app/main.py':
        content = re.sub(r'import json\n', '', content)
        content = re.sub(r'from typing import .*Any.*\n', '', content)
    
    # Fix blank lines with whitespace (W293)
    content = re.sub(r' +\n', '\n', content)
    
    # Fix expected 2 blank lines (E302/E305)
    content = re.sub(r'(\n)class', r'\n\n\nclass', content)
    content = re.sub(r'(\n)def', r'\n\n\ndef', content)
    
    # Fix extra blank lines - normalize to max 2 consecutive blank lines
    content = re.sub(r'\n{4,}', r'\n\n\n', content)
    
    # Fix trailing whitespace (W291)
    content = re.sub(r' +$', '', content, flags=re.MULTILINE)
    
    # Fix line length issues (E501) - this is more complex and would need manual review
    # Here we just identify them
    long_lines = []
    for i, line in enumerate(content.splitlines()):
        if len(line) > 79:
            long_lines.append((i+1, line))
    
    if long_lines:
        print(f"  Warning: {len(long_lines)} lines are too long in {file_path}. Manual review needed.")
        for line_num, line in long_lines[:3]:  # Show first 3 examples
            print(f"  Line {line_num}: {line[:50]}...")
    
    # Ensure file ends with exactly one newline
    content = content.rstrip('\n') + '\n'
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(long_lines)

def main():
    dirs_to_check = ['src', 'tests']
    files_fixed = 0
    files_with_long_lines = 0
    
    for dir_path in dirs_to_check:
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    long_lines = fix_file(file_path)
                    files_fixed += 1
                    if long_lines > 0:
                        files_with_long_lines += 1
    
    print(f"\nFixed formatting issues in {files_fixed} files.")
    if files_with_long_lines > 0:
        print(f"WARNING: {files_with_long_lines} files still have lines exceeding 79 characters.")
        print("These will need to be fixed manually or by using a tool like 'black'.")
    
    print("\nTo fix remaining issues, you might want to install and run:")
    print("  pip install black")
    print("  black --line-length 79 src/ tests/")

if __name__ == "__main__":
    main() 