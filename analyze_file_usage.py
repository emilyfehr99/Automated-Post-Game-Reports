#!/usr/bin/env python3
"""
Analyze Cascade Projects to identify used vs unused files
"""

import os
import re
from collections import defaultdict, Counter
from pathlib import Path

def get_python_files(root_dir):
    """Get all Python files, excluding virtual environments and common directories to skip."""
    python_files = []
    skip_dirs = {'.venv', 'venv', 'node_modules', '__pycache__', '.git', '.pytest_cache', 'build', 'dist'}
    
    for root, dirs, files in os.walk(root_dir):
        # Remove directories we want to skip
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def extract_imports(file_path):
    """Extract import statements from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        imports = set()
        
        # Pattern for various import styles
        patterns = [
            r'from\s+([^\s]+)\s+import',  # from module import
            r'import\s+([^\s,]+)',       # import module
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Clean up the import name
                module_name = match.strip()
                if module_name:
                    imports.add(module_name)
        
        return imports
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return set()

def is_standard_library(module_name):
    """Check if a module is from the standard library or common third-party packages."""
    stdlib_modules = {
        'os', 'sys', 'json', 'time', 'datetime', 'logging', 'requests', 'numpy', 'pandas', 
        'matplotlib', 'seaborn', 'selenium', 'reportlab', 'PIL', 'pathlib', 'collections',
        'typing', 're', 'math', 'io', 'sqlite3', 'schedule', 'argparse', 'subprocess',
        'threading', 'multiprocessing', 'urllib', 'http', 'email', 'csv', 'xml',
        'hashlib', 'base64', 'uuid', 'random', 'statistics', 'functools', 'itertools',
        'operator', 'copy', 'pickle', 'socket', 'ssl', 'ftplib', 'smtplib', 'poplib',
        'imaplib', 'telnetlib', 'gzip', 'bz2', 'zipfile', 'tarfile', 'shutil', 'glob',
        'fnmatch', 'tempfile', 'fileinput', 'linecache', 'filecmp', 'stat', 'filelock',
        'turtle', 'tkinter', 'winsound', 'wave', 'sunau', 'aifc', 'audioop', 'ossaudiodev',
        'colorsys', 'imghdr', 'sndhdr', 'wave', 'sunau', 'aifc', 'audioop', 'ossaudiodev',
        'wave', 'sunau', 'aifc', 'audioop', 'ossaudiodev', 'wave', 'sunau', 'aifc',
        'audioop', 'ossaudiodev', 'wave', 'sunau', 'aifc', 'audioop', 'ossaudiodev'
    }
    
    # Check if it's a standard library module
    if module_name.split('.')[0] in stdlib_modules:
        return True
    
    # Check if it's a common third-party package
    third_party = {
        'requests', 'numpy', 'pandas', 'matplotlib', 'seaborn', 'selenium', 'reportlab',
        'PIL', 'flask', 'django', 'fastapi', 'streamlit', 'plotly', 'bokeh', 'dash',
        'scipy', 'sklearn', 'tensorflow', 'torch', 'keras', 'opencv', 'cv2', 'bs4',
        'beautifulsoup4', 'lxml', 'xml', 'etree', 'webdriver_manager', 'schedule',
        'discord', 'telegram', 'twilio', 'sendgrid', 'boto3', 'psycopg2', 'sqlalchemy',
        'alembic', 'pytest', 'unittest', 'mock', 'nose', 'tox', 'coverage', 'black',
        'flake8', 'pylint', 'mypy', 'isort', 'pre_commit', 'click', 'typer', 'rich',
        'tqdm', 'colorama', 'termcolor', 'pyfiglet', 'art', 'emoji', 'fire', 'docopt',
        'plac', 'cement', 'cliff', 'pycli', 'invoke', 'fabric', 'ansible', 'salt'
    }
    
    if module_name.split('.')[0] in third_party:
        return True
    
    return False

def find_module_file(module_name, python_files):
    """Find the actual file corresponding to a module name."""
    # Remove .py extension if present
    if module_name.endswith('.py'):
        module_name = module_name[:-3]
    
    # Try different variations
    candidates = [
        f"{module_name}.py",
        f"{module_name}/__init__.py",
        f"{module_name.replace('.', '/')}.py",
        f"{module_name.replace('.', '/')}/__init__.py"
    ]
    
    for candidate in candidates:
        for py_file in python_files:
            if py_file.endswith(candidate):
                return py_file
    
    return None

def analyze_file_usage(root_dir):
    """Analyze which files are used vs unused."""
    print(f"Analyzing files in: {root_dir}")
    
    # Get all Python files
    python_files = get_python_files(root_dir)
    print(f"Found {len(python_files)} Python files")
    
    # Track imports and usage
    file_imports = {}
    imported_files = set()
    files_with_main = set()
    
    # Analyze each file
    for file_path in python_files:
        # Check if file has main execution
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "if __name__ == '__main__':" in content:
                    files_with_main.add(file_path)
        except:
            pass
        
        # Extract imports
        imports = extract_imports(file_path)
        file_imports[file_path] = imports
        
        # Find which local files are imported
        for module_name in imports:
            if not is_standard_library(module_name):
                module_file = find_module_file(module_name, python_files)
                if module_file:
                    imported_files.add(module_file)
    
    # Categorize files
    used_files = imported_files | files_with_main
    unused_files = set(python_files) - used_files
    
    # Additional analysis
    entry_points = files_with_main
    library_files = imported_files - files_with_main
    
    return {
        'total_files': len(python_files),
        'used_files': used_files,
        'unused_files': unused_files,
        'entry_points': entry_points,
        'library_files': library_files,
        'file_imports': file_imports
    }

def main():
    root_dir = "/Users/emilyfehr8/CascadeProjects"
    
    if not os.path.exists(root_dir):
        print(f"Directory {root_dir} does not exist!")
        return
    
    results = analyze_file_usage(root_dir)
    
    print("\n" + "="*80)
    print("CASCADE PROJECTS FILE USAGE ANALYSIS")
    print("="*80)
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total Python files: {results['total_files']}")
    print(f"  Used files: {len(results['used_files'])}")
    print(f"  Unused files: {len(results['unused_files'])}")
    print(f"  Entry points (with main): {len(results['entry_points'])}")
    print(f"  Library files (imported): {len(results['library_files'])}")
    
    print(f"\n🚀 ENTRY POINTS ({len(results['entry_points'])}):")
    for file_path in sorted(results['entry_points']):
        rel_path = os.path.relpath(file_path, root_dir)
        print(f"  • {rel_path}")
    
    print(f"\n📚 LIBRARY FILES ({len(results['library_files'])}):")
    for file_path in sorted(results['library_files']):
        rel_path = os.path.relpath(file_path, root_dir)
        print(f"  • {rel_path}")
    
    print(f"\n🗑️  POTENTIALLY UNUSED FILES ({len(results['unused_files'])}):")
    for file_path in sorted(results['unused_files']):
        rel_path = os.path.relpath(file_path, root_dir)
        print(f"  • {rel_path}")
    
    # Show top importers
    print(f"\n🔗 TOP FILES BY IMPORT COUNT:")
    import_counts = Counter()
    for file_path, imports in results['file_imports'].items():
        local_imports = 0
        for module_name in imports:
            if not is_standard_library(module_name):
                module_file = find_module_file(module_name, get_python_files(root_dir))
                if module_file:
                    local_imports += 1
        if local_imports > 0:
            import_counts[os.path.relpath(file_path, root_dir)] = local_imports
    
    for file_path, count in import_counts.most_common(10):
        print(f"  • {file_path}: {count} local imports")
    
    # Show most imported files
    print(f"\n⭐ MOST IMPORTED FILES:")
    import_frequency = Counter()
    for file_path, imports in results['file_imports'].items():
        for module_name in imports:
            if not is_standard_library(module_name):
                module_file = find_module_file(module_name, get_python_files(root_dir))
                if module_file:
                    import_frequency[os.path.relpath(module_file, root_dir)] += 1
    
    for file_path, count in import_frequency.most_common(10):
        print(f"  • {file_path}: imported by {count} files")

if __name__ == "__main__":
    main()
