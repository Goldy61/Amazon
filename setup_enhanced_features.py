#!/usr/bin/env python3
"""
Setup script for enhanced e-commerce features
This script will add the new database tables and columns needed for:
- Product Reviews & Ratings
- Wishlist
- Newsletter Subscriptions
- Product Views Tracking
"""

import pymysql
from config import Config

def setup_enhanced_features():
    """Run the enhanced features database migration"""
    
    print("=" * 70)
    print("ShopHub Enhanced Features Setup")
    print("=" * 70)
    print()
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        print()
        
        # Read SQL file
        print("📄 Reading migration file...")
        with open('database/add_enhanced_features.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"📝 Found {len(statements)} SQL statements to execute")
        print()
        
        # Execute each statement
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            # Skip comments and USE statements
            if statement.startswith('--') or statement.startswith('/*') or statement.upper().startswith('USE'):
                continue
            
            try:
                cursor.execute(statement)
                conn.commit()
                
                # Determine what was created
                if 'CREATE TABLE' in statement.upper():
                    table_name = statement.split('TABLE')[1].split('(')[0].strip().split()[0]
                    if 'IF NOT EXISTS' in statement.upper():
                        table_name = table_name.replace('IF', '').replace('NOT', '').replace('EXISTS', '').strip()
                    print(f"✅ [{i}/{len(statements)}] Created table: {table_name}")
                    success_count += 1
                elif 'ALTER TABLE' in statement.upper():
                    table_name = statement.split('TABLE')[1].split('ADD')[0].strip()
                    print(f"✅ [{i}/{len(statements)}] Altered table: {table_name}")
                    success_count += 1
                elif 'CREATE OR REPLACE VIEW' in statement.upper():
                    view_name = statement.split('VIEW')[1].split('AS')[0].strip()
                    print(f"✅ [{i}/{len(statements)}] Created view: {view_name}")
                    success_count += 1
                elif 'INSERT' in statement.upper():
                    print(f"✅ [{i}/{len(statements)}] Inserted sample data")
                    success_count += 1
                elif 'UPDATE' in statement.upper():
                    print(f"✅ [{i}/{len(statements)}] Updated data")
                    success_count += 1
                else:
                    success_count += 1
                    
            except pymysql.err.OperationalError as e:
                if 'Duplicate column name' in str(e) or 'already exists' in str(e):
                    print(f"⏭️  [{i}/{len(statements)}] Skipped (already exists)")
                    skip_count += 1
                else:
                    print(f"❌ [{i}/{len(statements)}] Error: {e}")
                    error_count += 1
            except Exception as e:
                if 'Duplicate entry' in str(e):
                    skip_count += 1
                else:
                    print(f"❌ [{i}/{len(statements)}] Error: {e}")
                    error_count += 1
        
        print()
        print("=" * 70)
        print("Setup Summary:")
        print(f"  ✅ Successful: {success_count}")
        print(f"  ⏭️  Skipped: {skip_count}")
        print(f"  ❌ Errors: {error_count}")
        print("=" * 70)
        print()
        
        if error_count == 0:
            print("🎉 Enhanced features setup completed successfully!")
            print()
            print("New features available:")
            print("  ⭐ Product Reviews & Ratings")
            print("  ❤️  Wishlist/Favorites")
            print("  📧 Newsletter Subscriptions")
            print("  👁️  Product Views Tracking")
            print()
            print("You can now:")
            print("  1. Add products to wishlist")
            print("  2. Write reviews for purchased products")
            print("  3. Subscribe to newsletter")
            print("  4. View product statistics")
        else:
            print("⚠️  Setup completed with some errors.")
            print("Please check the error messages above.")
        
        cursor.close()
        conn.close()
        
    except FileNotFoundError:
        print("❌ Error: Could not find 'database/add_enhanced_features.sql'")
        print("Make sure you're running this script from the project root directory.")
    except pymysql.err.OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print("Please check your database configuration in config.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    setup_enhanced_features()
