# check how many lines are in this folder for files that end with .py including cog subfolder
import os
import glob

from pathlib import Path

def count_lines_in_file(file_path):
    """Count the number of lines in a single file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        return len(non_empty_lines)

def count_lines_in_directory(directory):
    """Count the number of lines in all .py files in a directory and its subdirectories."""
    total_lines = 0
    excluded_dirs = ['__pycache__', '.git', 'pyvenv', 'lib', 'site-packages', 'Lib', 'venv']
    
    dir_path = Path(directory)
    
    for py_file in dir_path.glob('**/*.py'):
        if any(excluded in part for part in py_file.parts for excluded in excluded_dirs):
            continue
            
        total_lines += count_lines_in_file(py_file)
    
    return total_lines

current_dir = Path('.')
root_lines = count_lines_in_directory(current_dir)

print(f'Total lines in root: {root_lines}')