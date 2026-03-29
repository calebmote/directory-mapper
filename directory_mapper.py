#!/usr/bin/env python3
"""
Directory Mapper - Recursively maps directory structure and file contents

Example commands:
python directory_mapper.py C:\\path\\to\\directory --excel directory_map.xlsx
python directory_mapper.py C:\\path\\to\\directory -o output.json -e output.xlsx

# Skip files larger than 10MB
python directory_mapper.py D:\ --max-size 10485760 -e D_drive_map.xlsx

# Skip files larger than 100MB  
python directory_mapper.py D:\ --max-size 104857600 -e D_drive_map.xlsx

# Skip files larger than 1GB
python directory_mapper.py D:\ --max-size 1073741824 -e directory-map-21-Mar-2026.xlsx
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
import mimetypes
import json
from datetime import datetime
import time
import hashlib
from exclude_list import EXCLUDE_RULES


class DirectoryMapper:
    def __init__(self, root_path: str, include_content: bool = True, 
                 max_file_size: int = 1024 * 1024, exclude_patterns: List[str] = None):
        self.root_path = Path(root_path).resolve()
        self.include_content = include_content
        self.max_file_size = max_file_size
        self.exclude_patterns = exclude_patterns or ['.git', '__pycache__', '.vscode', 'node_modules']
        self.external_excludes = self.load_external_excludes()
        self.directory_map = {}
        self.total_files = 0
        self.processed_files = 0
        self.total_directories = 0
        self.processed_directories = 0
        self.start_time = None
        
    def load_external_excludes(self) -> List[str]:
        """Load exclude patterns from EXCLUDE_RULES dictionary"""
        excludes = []
        try:
            for category, rules in EXCLUDE_RULES.items():
                patterns = rules.get('patterns', [])
                excludes.extend(patterns)
                print(f"Loaded {len(patterns)} patterns from {category}")
            
            print(f"Total external exclude patterns: {len(excludes)}")
            return excludes
        except Exception as e:
            print(f"Warning: Could not load exclude rules: {e}")
            return []
    
    def count_items(self, current_path: Path = None) -> None:
        """Count total files and directories for progress tracking"""
        if current_path is None:
            current_path = self.root_path
            
        if self.should_exclude(current_path):
            return
            
        if current_path.is_file():
            self.total_files += 1
        elif current_path.is_dir():
            self.total_directories += 1
            try:
                for item in current_path.iterdir():
                    if not self.should_exclude(item):
                        self.count_items(item)
            except (PermissionError, OSError):
                pass
    
    def print_progress(self, current_item: str, is_file: bool = True) -> None:
        """Print progress bar and status"""
        if is_file:
            self.processed_files += 1
        else:
            self.processed_directories += 1
            
        total_items = self.total_files + self.total_directories
        processed_items = self.processed_files + self.processed_directories
        
        if total_items > 0:
            percentage = (processed_items / total_items) * 100
            elapsed = time.time() - self.start_time if self.start_time else 0
            
            # Estimate remaining time
            if processed_items > 0:
                avg_time_per_item = elapsed / processed_items
                remaining_items = total_items - processed_items
                eta_seconds = avg_time_per_item * remaining_items
                eta_str = f"{eta_seconds:.0f}s" if eta_seconds < 60 else f"{eta_seconds/60:.1f}m"
            else:
                eta_str = "calculating..."
            
            # Create progress bar
            bar_length = 40
            filled_length = int(bar_length * percentage / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Clear line and print progress
            print(f"\r[{bar}] {percentage:.1f}% | {processed_items}/{total_items} | ETA: {eta_str} | Processing: {current_item[:50]}{'...' if len(current_item) > 50 else ''}", end='', flush=True)
    
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded based on patterns"""
        path_str = str(path)
        
        # Check if path contains any exclude pattern from command line
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        
        # Check if path contains any pattern from external exclude file
        for pattern in self.external_excludes:
            if pattern in path_str:
                return True
            
        return False
    
    def calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """Calculate hash of file content for duplicate detection"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception:
            # Return empty string for files that can't be hashed (binary files, permission issues, etc.)
            return ""
    
    def is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
        
        # Check common text file extensions
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', 
                          '.md', '.yml', '.yaml', '.ini', '.cfg', '.log', '.csv'}
        return file_path.suffix.lower() in text_extensions
    
    def read_file_content(self, file_path: Path) -> str:
        """Read file content with error handling"""
        try:
            if file_path.stat().st_size > self.max_file_size:
                return f"[File too large ({file_path.stat().st_size} bytes) - content skipped]"
            
            if not self.is_text_file(file_path):
                return f"[Binary file - content not displayed]"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return content if content.strip() else "[Empty file]"
                
        except Exception as e:
            return f"[Error reading file: {str(e)}]"
    
    def map_directory(self, current_path: Path = None) -> Dict[str, Any]:
        """Recursively map directory structure and contents"""
        if current_path is None:
            current_path = self.root_path
            self.start_time = time.time()
            print("Counting items for progress tracking...")
            self.count_items()
            print(f"Found {self.total_files} files and {self.total_directories} directories")
            print("Starting mapping...")
            
        if self.should_exclude(current_path):
            return {}
        
        # Print progress
        relative_path = str(current_path.relative_to(self.root_path))
        self.print_progress(relative_path, current_path.is_file())
        
        result = {
            'type': 'directory' if current_path.is_dir() else 'file',
            'path': str(current_path.relative_to(self.root_path)),
            'name': current_path.name,
            'size': None,
            'content': None,
            'hash': None,
            'children': {}
        }
        
        try:
            stat_info = current_path.stat()
            result['size'] = stat_info.st_size
            
            if current_path.is_file() and self.include_content:
                result['content'] = self.read_file_content(current_path)
                result['hash'] = self.calculate_file_hash(current_path)
            
            elif current_path.is_dir():
                for item in sorted(current_path.iterdir()):
                    if not self.should_exclude(item):
                        child_result = self.map_directory(item)
                        if child_result:
                            result['children'][item.name] = child_result
                            
        except PermissionError:
            result['error'] = "[Permission denied]"
        except Exception as e:
            result['error'] = f"[Error: {str(e)}]"
        
        return result
    
    def print_map(self, data: Dict[str, Any], indent: int = 0, show_content: bool = True) -> None:
        """Print the directory map in a readable format"""
        prefix = "  " * indent
        
        if data['type'] == 'directory':
            print(f"{prefix}📁 {data['name']}/")
            if 'error' in data:
                print(f"{prefix}   {data['error']}")
            
            for child_name, child_data in data.get('children', {}).items():
                self.print_map(child_data, indent + 1, show_content)
        else:
            size_str = f" ({data['size']} bytes)" if data['size'] else ""
            print(f"{prefix}📄 {data['name']}{size_str}")
            
            if 'error' in data:
                print(f"{prefix}   {data['error']}")
            elif show_content and data.get('content') is not None:
                content = data['content']
                if content and not content.startswith('['):
                    lines = content.split('\n')
                    if len(lines) > 10:
                        print(f"{prefix}   Content (first 10 lines):")
                        for line in lines[:10]:
                            print(f"{prefix}   {line}")
                        print(f"{prefix}   ... ({len(lines) - 10} more lines)")
                    else:
                        print(f"{prefix}   Content:")
                        for line in lines:
                            print(f"{prefix}   {line}")
                else:
                    print(f"{prefix}   {content}")
    
    def save_to_file(self, data: Dict[str, Any], output_path: str) -> None:
        """Save the directory map to a file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_to_excel(self, data: Dict[str, Any], output_path: str) -> None:
        """Save the directory map to an Excel file"""
        try:
            import pandas as pd
        except ImportError:
            print("Error: pandas library is required for Excel output. Install with: pip install pandas openpyxl")
            return
        
        rows = []
        self._flatten_directory_tree(data, rows)
        
        df = pd.DataFrame(rows)
        
        # Save to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Directory Map', index=False)
            
            # Adjust column widths
            worksheet = writer.sheets['Directory Map']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _flatten_directory_tree(self, data: Dict[str, Any], rows: List[Dict], parent_path: str = "", level: int = 0) -> None:
        """Flatten directory tree into tabular format for Excel"""
        item_path = f"{parent_path}/{data['name']}" if parent_path else data['name']
        
        row = {
            'Level': level,
            'Type': data['type'].title(),
            'Name': data['name'],
            'Full Path': item_path,
            'Size (bytes)': data.get('size', 0),
            'Modified': datetime.fromtimestamp(Path(self.root_path / data['path']).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S') if data['path'] != '.' else '',
            'Hash': data.get('hash', ''),
            'Content Preview': ''
        }
        
        if data['type'] == 'file' and data.get('content'):
            content = data['content']
            if not content.startswith('['):
                # Truncate content for preview and remove invalid Excel characters
                preview = content.replace('\n', ' ')[:200]
                if len(content) > 200:
                    preview += '...'
                # Remove characters that are invalid in Excel
                invalid_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x0b', '\x0c', '\x0d', '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f']
                for char in invalid_chars:
                    preview = preview.replace(char, '')
                row['Content Preview'] = preview
            else:
                row['Content Preview'] = content
        
        rows.append(row)
        
        # Process children
        for child_name, child_data in data.get('children', {}).items():
            self._flatten_directory_tree(child_data, rows, item_path, level + 1)


def main():
    parser = argparse.ArgumentParser(description='Map directory structure and contents')
    parser.add_argument('directory', help='Directory to map')
    parser.add_argument('--no-content', action='store_true', 
                       help='Do not include file contents')
    parser.add_argument('--max-size', type=int, default=1024*1024,
                       help='Maximum file size to read in bytes (default: 1MB)')
    parser.add_argument('--exclude', nargs='*', default=['.git', '__pycache__', '.vscode', 'node_modules'],
                       help='Patterns to exclude')
    parser.add_argument('--output', '-o', help='Output file (JSON format). Defaults to directory_map.json')
    parser.add_argument('--excel', '-e', help='Output Excel file (.xlsx format)')
    parser.add_argument('--no-display', action='store_true',
                       help='Do not display content in terminal output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    mapper = DirectoryMapper(
        root_path=args.directory,
        include_content=not args.no_content,
        max_file_size=args.max_size,
        exclude_patterns=args.exclude
    )
    
    print(f"Mapping directory: {mapper.root_path}")
    print("=" * 60)
    
    directory_map = mapper.map_directory()
    
    # Print completion message
    total_time = time.time() - mapper.start_time if mapper.start_time else 0
    print(f"\n\nMapping completed in {total_time:.1f} seconds!")
    print(f"Processed {mapper.processed_files} files and {mapper.processed_directories} directories")
    
    # Set default output file if not provided
    if args.output or not args.excel:
        output_file = args.output or "directory_map.json"
        print(f"\nSaving JSON output...")
        mapper.save_to_file(directory_map, output_file)
        print(f"JSON map saved to: {output_file}")
    
    if args.excel:
        print(f"Saving Excel output...")
        mapper.save_to_excel(directory_map, args.excel)
        print(f"Excel map saved to: {args.excel}")
    
    if not args.no_display:
        print("\nDirectory Structure:")
        print("-" * 40)
        mapper.print_map(directory_map, show_content=not args.no_content)


if __name__ == "__main__":
    main()
