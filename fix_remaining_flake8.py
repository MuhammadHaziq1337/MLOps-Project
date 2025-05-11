#!/usr/bin/env python
import re


def fix_unused_imports(file_path, imports_to_remove):
    print(f"Fixing unused imports in {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for import_pattern in imports_to_remove:
        content = re.sub(import_pattern, '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_undefined_names(file_path, imports_to_add):
    print(f"Adding missing imports in {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the last import statement
    import_lines = re.findall(r'^.*import.*$', content, re.MULTILINE)
    if import_lines:
        last_import = import_lines[-1]
        # Add new imports after the last import
        content = content.replace(last_import, last_import + '\n' + imports_to_add)
    else:
        # If no imports found, add at the beginning
        content = imports_to_add + '\n' + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Fix files with unused imports
    files_with_unused_imports = {
        'src/app/metrics.py': [
            r'from typing import Optional.*\n',
        ],
        'src/data/process.py': [
            r'from pathlib import Path.*\n',
        ],
        'src/models/run_training.py': [
            r'from pathlib import Path.*\n',
        ],
        'tests/test_metrics.py': [
            r'import time.*\n',
            r'from prometheus_client import Counter, Gauge, Histogram, Summary.*\n',
            r'from starlette.responses import Response.*\n',
        ]
    }
    
    for file_path, imports in files_with_unused_imports.items():
        fix_unused_imports(file_path, imports)
    
    # Fix files with undefined names
    files_with_undefined_names = {
        'src/app/main.py': 'from typing import Dict, Optional',
    }
    
    for file_path, imports in files_with_undefined_names.items():
        fix_undefined_names(file_path, imports)
    
    print("\nManual fixes still needed for:")
    print("1. Line length issues (E501) - run black again or fix manually")
    print("2. Unused variable in tests/test_metrics.py line 109: expected_mean_feature1")
    print("3. Unused global in src/app/metrics.py: _PREDICTIONS_BUFFER")
    
    print("\nTo fix line length issues:")
    print("black --line-length 79 src/ tests/")

if __name__ == "__main__":
    main() 