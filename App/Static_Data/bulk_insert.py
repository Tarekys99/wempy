import json
import sys
from pathlib import Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# إضافة المجلد الأب (App) إلى Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Database.db_connect import engine

import Database.models.user_model
import Database.models.shift_model
import Database.models.payment_model
import Database.models.orders_info_model
import Database.models.order_item_model
import Database.models.product_model
from Database.models.address_zone_model import DeliveryZone

# cd App\Static_Data
# python bulk_insert.py

base_path = Path(__file__).resolve().parent
json_path = base_path / "delivery_zones.json"

print(f"📂 Reading data from: {json_path}")

with json_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

print(f"📊 Found {len(data)} delivery zones to insert")

with Session(engine) as session:
    try:
        session.bulk_insert_mappings(DeliveryZone, data)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        print(f"⚠️ Insert failed: duplicate zone names detected.")
        print(f"   Error details: {exc}")
    except Exception as exc:
        session.rollback()
        print(f"⚠️ Insert failed: {exc}")
    else:
        print(f"✅ Successfully inserted {len(data)} delivery zones!")