# Directory Mapper

A powerful Python script that recursively maps directory structures and file contents with advanced features like progress tracking, duplicate detection, and flexible output formats.

## Features

- **Recursive Directory Mapping**: Scans entire directory trees with file content analysis
- **Progress Tracking**: Real-time progress bar with ETA calculation
- **Multiple Output Formats**: JSON and Excel (XLSX) support
- **File Hashing**: SHA-256 hash calculation for duplicate detection
- **Flexible Exclusion System**: Organized exclude patterns by category
- **Content Analysis**: Reads and displays text file contents
- **Size Filtering**: Skip files larger than specified size

## Installation

### Prerequisites

- Python 3.7 or higher
- Required packages: `pandas`, `openpyxl`

### Install Dependencies

```bash
pip install pandas openpyxl
```

## Usage

### Basic Usage

```bash
# Map directory with default settings
python directory_mapper.py C:\path\to\directory

# Output to Excel file
python directory_mapper.py C:\path\to\directory -e output.xlsx

# Output to JSON file
python directory_mapper.py C:\path\to\directory -o output.json
```

### Advanced Options

```bash
# Map with custom exclude patterns
python directory_mapper.py C:\path\to\directory --exclude pattern1 pattern2

# Skip files larger than 10MB
python directory_mapper.py C:\path\to\directory --max-size 10485760

# Don't include file contents (faster processing)
python directory_mapper.py C:\path\to\directory --no-content

# Hide terminal display
python directory_mapper.py C:\path\to\directory --no-display
```

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `directory` | - | Directory to map | Required |
| `--output` | `-o` | JSON output file | `directory_map.json` |
| `--excel` | `-e` | Excel output file (.xlsx) | None |
| `--exclude` | - | Exclude patterns (space-separated) | `.git __pycache__ .vscode node_modules` |
| `--max-size` | - | Max file size to read (bytes) | `1048576` (1MB) |
| `--no-content` | - | Skip file content reading | `False` |
| `--no-display` | - | Hide terminal output | `False` |

## Exclude Patterns

The script uses `exclude_list.py` to organize exclusion patterns by category:

```python
EXCLUDE_RULES = {
    'File_Extensions': {
        'patterns': [
            '.angular',
            '.htm', 
            '.xml',
            '.tmp',
            '.venv'
        ]
    },
    'Directories': {
        'patterns': [
            'Kiwix',
            'OEBPS',
            'Movies',
            'RECYCLE.BIN'
        ]
    },
    'System_Files': {
        'patterns': [
            '$RECYCLE.BIN',
            'System Volume Information',
            'Desktop.ini'
        ]
    }
}
```

### Customizing Excludes

Edit `exclude_list.py` to add or modify exclusion patterns:

1. **Add new categories**: Create new keys in the `EXCLUDE_RULES` dictionary
2. **Modify patterns**: Add/remove patterns in the `patterns` lists
3. **Comment out patterns**: Use `#` to temporarily disable patterns

## Output Formats

### JSON Output

```json
{
  "type": "directory",
  "path": ".",
  "name": "root",
  "size": 0,
  "content": null,
  "hash": null,
  "children": {
    "file.txt": {
      "type": "file",
      "path": "file.txt",
      "name": "file.txt",
      "size": 1024,
      "content": "File content here...",
      "hash": "sha256_hash_here",
      "children": {}
    }
  }
}
```

### Excel Output

The Excel file contains the following columns:

- **Level**: Directory depth level
- **Type**: File or Directory
- **Name**: File/directory name
- **Full Path**: Complete path relative to root
- **Size (bytes)**: File size
- **Modified**: Last modification timestamp
- **Hash**: SHA-256 hash (for files)
- **Content Preview**: First 200 characters of file content

## Examples

### Example 1: Map Entire Drive

```bash
# Map D: drive to Excel with progress tracking
python directory_mapper.py D:\ -e D_drive_map.xlsx
```

### Example 2: Quick Scan Without Content

```bash
# Fast scan without reading file contents
python directory_mapper.py C:\Users --no-content -o users_structure.json
```

### Example 3: Large File Analysis

```bash
# Include files up to 100MB
python directory_mapper.py C:\Projects --max-size 104857600 -e projects.xlsx
```

## Performance Considerations

- **Large Directories**: Use `--no-content` for faster scanning
- **File Size**: Increase `--max-size` to include larger files
- **Exclusions**: Customize `exclude_list.py` to skip unnecessary directories
- **Memory Usage**: Script processes files in chunks to handle large files efficiently

## Troubleshooting

### Common Issues

1. **Permission Denied**: The script handles permission errors gracefully and continues processing
2. **Large Files**: Files larger than `--max-size` are skipped but still listed in output
3. **Binary Files**: Binary files show as `[Binary file - content not displayed]`
4. **Missing Dependencies**: Install required packages with `pip install pandas openpyxl`

### Error Messages

- `Error: Directory 'X' does not exist`: Check that the directory path is correct
- `Warning: Could not load exclude rules`: Verify `exclude_list.py` exists and has correct syntax
- `ModuleNotFoundError: No module named 'pandas'`: Install missing dependencies

## File Structure

```
directory-mapper/
├── directory_mapper.py    # Main script
├── exclude_list.py        # Exclude patterns configuration
└── README.md              # This documentation
```

## License

This project is open source and available under the MIT License.
