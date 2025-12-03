# import json
# import sys
# from pathlib import Path
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import Session

# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# from Database.db_connect import engine

# # Import models in correct order to resolve relationships
# import Database.models.product_model
# import Database.models.address_zone_model
# import Database.models.user_model
# import Database.models.shift_model
# import Database.models.payment_model
# import Database.models.orders_info_model
# import Database.models.order_item_model
# from Database.models.product_model import Products

# # cd App\Static_Data
# # python bulk_insert_products.py

# base_path = Path(__file__).resolve().parent
# json_path = base_path / "sandwiches.json"

# print(f"📂 Reading data from: {json_path}")

# with json_path.open("r", encoding="utf-8") as f:
#     data = json.load(f)

# print(f"📊 Found {len(data)} sandwich to insert")

# # تحويل البيانات لتتوافق مع جدول products
# # نأخذ فقط ImageUrl و Name ونضيف CategoryID = 1
# products_data = []
# for sandwich in data:
#     product = {
#         "CategoryID": 2,
#         "Name": sandwich["Name"],
#         "ImageUrl": sandwich["ImageUrl"],
#         "Description": "لا وصف"
#     }
#     products_data.append(product)

# print(f"✨ Prepared {len(products_data)} products for insertion")

# with Session(engine) as session:
#     try:
#         session.bulk_insert_mappings(Products, products_data)
#         session.commit()
#     except IntegrityError as exc:
#         session.rollback()
#         print(f"⚠️ Insert failed: duplicate product names detected.")
#         print(f"   Error details: {exc}")
#     except Exception as exc:
#         session.rollback()
#         print(f"⚠️ Insert failed: {exc}")
#     else:
#         print(f"✅ Successfully inserted {len(products_data)} products!")
