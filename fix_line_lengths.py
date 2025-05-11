#!/usr/bin/env python
import re

# Files with line length issues and the specific line numbers
files_to_fix = {
    'src/app/main.py': [66],
    'src/app/metrics.py': [4],
    'src/data/preprocessing.py': [38],
    'src/data/process.py': [1],
    'src/models/run_training.py': [20, 58],
    'tests/test_data_preprocessing.py': [110],
    'tests/test_docker_monitoring.py': [61],
    'tests/test_monitoring_k8s.py': [49, 107, 115]
}

def wrap_line(line_to_fix, max_length=79):
    """
    Break a long line into multiple lines.
    """
    # If it's a comment, wrap differently
    if line_to_fix.strip().startswith('#'):
        if len(line_to_fix) > max_length:
            # Split at a space before max_length
            space_pos = line_to_fix.rfind(' ', 0, max_length)
            if space_pos > 0:
                return line_to_fix[:space_pos] + '\n# ' + line_to_fix[space_pos+1:]
    
    # For docstrings, wrap with """
    if '"""' in line_to_fix and len(line_to_fix) > max_length:
        split_pos = line_to_fix.rfind(' ', 0, max_length)
        if split_pos > 0:
            return line_to_fix[:split_pos] + '"\n"""' + line_to_fix[split_pos+1:]
    
    # If it contains parentheses, try to break at a comma inside parentheses
    if '(' in line_to_fix and ')' in line_to_fix:
        for i in range(max_length, 0, -1):
            if i < len(line_to_fix) and line_to_fix[i] == ',':
                indent = len(line_to_fix) - len(line_to_fix.lstrip())
                return line_to_fix[:i+1] + '\n' + ' ' * (indent + 4) + line_to_fix[i+1:].lstrip()
    
    # If no other pattern applies, just insert a line break at max length
    if len(line_to_fix) > max_length:
        return line_to_fix[:max_length] + '\\\n' + line_to_fix[max_length:]
    
    return line_to_fix

def fix_file(file_path, line_numbers):
    print(f"Fixing line lengths in {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Adjust line numbers to be 0-indexed
    line_numbers = [n - 1 for n in line_numbers]
    
    for line_idx in line_numbers:
        if line_idx < len(lines):
            original_line = lines[line_idx]
            if len(original_line.rstrip('\n')) > 79:
                fixed_line = wrap_line(original_line.rstrip('\n'))
                if '\n' in fixed_line:
                    lines[line_idx] = fixed_line + '\n'
                else:
                    lines[line_idx] = fixed_line + '\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print(f"Fixed {file_path}")

def main():
    for file_path, line_numbers in files_to_fix.items():
        fix_file(file_path, line_numbers)
    
    print("\nLine length fixes applied! Run flake8 to verify.")

if __name__ == "__main__":
    main() 