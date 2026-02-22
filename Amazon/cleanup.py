#!/usr/bin/env python3
"""
Cleanup script to remove temporary files and Python cache
"""

import os
import shutil
import glob

def cleanup_pycache():
    """Remove all __pycache__ directories"""
    removed_count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"✅ Removed: {pycache_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {pycache_path}: {e}")
    
    return removed_count

def cleanup_temp_files():
    """Remove temporary files"""
    patterns = ['*.tmp', '*.bak', '*.backup', '*.old', '*.pyc']
    removed_count = 0
    
    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
    
    return removed_count

def main():
    """Run cleanup"""
    print("🧹 Starting cleanup...")
    print("-" * 40)
    
    # Clean Python cache
    pycache_count = cleanup_pycache()
    
    # Clean temporary files
    temp_count = cleanup_temp_files()
    
    print("-" * 40)
    print(f"🎯 Cleanup complete!")
    print(f"   - Removed {pycache_count} __pycache__ directories")
    print(f"   - Removed {temp_count} temporary files")
    print()
    print("💡 Tip: Use 'python generate_placeholder.py [style]' to create new placeholders!")
    print("   Available styles: crazy, neon, galaxy, simple")

if __name__ == "__main__":
    main()