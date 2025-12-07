"""
Migration script to add IsSada column to order_items table
This adds support for the "سادة" (plain/without filling) option for sandwich orders

Usage:
    Run from the Backend directory:
    python App/Database/migrations/add_issada_column.py
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy import text
from App.Database import db_connect

def add_issada_column():
    """Add IsSada column to order_items table with default value False"""
    
    engine = db_connect.engine
    
    with engine.connect() as connection:
        # Add IsSada column with default value False
        connection.execute(text("""
            ALTER TABLE order_items 
            ADD COLUMN IF NOT EXISTS "IsSada" BOOLEAN NOT NULL DEFAULT FALSE;
        """))
        
        connection.commit()
        print("✅ Successfully added IsSada column to order_items table")

if __name__ == "__main__":
    print("Starting migration: Adding IsSada column to order_items table...")
    try:
        add_issada_column()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)
