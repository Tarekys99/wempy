# Database Migrations

## How to Run Migrations

### Add IsSada Column Migration

To add the IsSada column to the order_items table, run from the Backend directory:

```bash
python App/Database/migrations/add_issada_column.py
```

This migration will:
- Add a new `IsSada` column (Boolean) to the `order_items` table
- Set default value to `False` for all existing records
- Make the column NOT NULL with a default value

### Verification

After running the migration, you can verify it worked by:
1. Checking the database schema
2. Creating a new order with `IsSada: true` in the request
3. Retrieving the order and confirming the `IsSada` field is present

## Migration Details

**Migration**: `add_issada_column.py`
**Date**: 2024
**Purpose**: Add support for "سادة" (plain/without filling) option for sandwich orders
**Changes**:
- Adds `IsSada` BOOLEAN column to `order_items` table
- Sets default value to FALSE
- Column is NOT NULL
