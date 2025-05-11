#!/usr/bin/env python
import re


def fix_files():
    # Define the files to fix
    files_to_fix = [
        'src/__init__.py',
        'src/app/__init__.py',
        'src/app/main.py',
        'src/data/__init__.py',
        'src/data/preprocessing.py',
        'src/models/__init__.py',
        'src/models/train.py',
        'tests/__init__.py',
        'tests/test_app.py',
        'tests/test_data_preprocessing.py',
        'tests/test_model_train.py'
    ]
    
    for file_path in files_to_fix:
        print(f"Fixing {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Remove trailing whitespace
        content = re.sub(r' +$', '', content, flags=re.MULTILINE)
        
        # 2. Fix blank lines with whitespace
        content = re.sub(r' +\n', '\n', content)
        
        # 3. Fix blank line at end of file (exactly one newline at EOF)
        content = content.rstrip('\n') + '\n'
        
        # 4. Fixed unused imports in main.py
        if file_path == 'src/app/main.py':
            content = re.sub(r'import json\n', '', content)
            content = re.sub(r'from typing import.*Any.*\n', '', content)
        
        # 5. Fix spacing between functions and classes (2 blank lines)
        content = re.sub(r'\n(class|def)', r'\n\n\n\1', content)
        # Clean up excessive blank lines (max 2)
        content = re.sub(r'\n{4,}', r'\n\n\n', content)
        
        # Write back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")
    
    print("\nNow run the black formatter to fix line length issues:")
    print("pip install black")
    print("black --line-length 79 src/ tests/")

if __name__ == "__main__":
    fix_files() 