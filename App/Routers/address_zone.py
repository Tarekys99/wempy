from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging
import uuid

from Database.db_connect import get_db
from Database.models.address_zone_model import Address, DeliveryZone
from Database.pydantic_schema.address_zone_schema import (
    AddressCreate,
    AddressUpdate,
    AddressWithZone,
    ZoneCreate,
    ZoneResponse,
    ZoneUpdate
)

logger = logging.getLogger("address_zone")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 datefmt='%Y-%m-%d %H:%M:%S')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

address_router = APIRouter(prefix="/addresses", tags=["Addresses"])
zone_router = APIRouter(prefix="/zones", tags=["Delivery Zones"])

#=======================================
# Address Routers
#=======================================

@address_router.post("/create/{user_id}", response_model=AddressWithZone, status_code=status.HTTP_201_CREATED)
def create_address(
    user_id: uuid.UUID,
    address: AddressCreate,
    db: Session = Depends(get_db)
    ):
    logger.info(f"محاولة إضافة عنوان جديد للمستخدم ID: {user_id}")
    logger.debug(f"بيانات العنوان المستلمة: {address.model_dump()}")
    try:
        zone = db.query(DeliveryZone).filter(DeliveryZone.ZoneID == address.ZoneID).first()
        if not zone:
            logger.warning(f"✗ المنطقة غير موجودة - ZoneID: {address.ZoneID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="المنطقة غير موجودة"
            )
        db_address = Address(
            **address.model_dump(),
            UserID=user_id
        )
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        logger.info(f"✓ تم إضافة العنوان بنجاح - AddressID: {db_address.AddressID}, UserID: {user_id}")
        return db_address
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"✗ خطأ عند إضافة العنوان: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"فشل إضافة العنوان: {str(e)}")

# Get all addresses of a user
@address_router.get("/user/{user_id}", response_model=List[AddressWithZone])
def get_user_addresses(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
     ):
    logger.info(f"عرض عناوين المستخدم ID: {user_id}")
    addresses = db.query(Address).filter(
        Address.UserID == user_id
    ).order_by(Address.AddressID.asc()).all()
    logger.info(f"✓ تم جلب {len(addresses)} عنوان للمستخدم {user_id}")
    return addresses

# Get a specific address of a user
@address_router.get("/detail/{user_id}/{address_id}", response_model=AddressWithZone)
def get_address_detail(
    user_id: uuid.UUID,
    address_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"طلب عرض العنوان AddressID: {address_id}, UserID: {user_id}")
    db_address = db.query(Address).filter(
        Address.AddressID == address_id,
        Address.UserID == user_id
    ).first()
    if not db_address:
        logger.warning(f"✗ العنوان غير موجود - AddressID: {address_id}, UserID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="العنوان غير موجود")
    logger.info(f"✓ تم جلب العنوان - AddressID: {address_id}")
    return db_address

# Update an address
@address_router.put("/update/{user_id}/{address_id}", response_model=AddressWithZone)
def update_address(
    user_id: uuid.UUID,
    address_id: int,
    address_update: AddressUpdate,
    db: Session = Depends(get_db)
     ):
    logger.info(f"محاولة تحديث العنوان AddressID: {address_id}, UserID: {user_id}")
    db_address = db.query(Address).filter(
        Address.AddressID == address_id,
        Address.UserID == user_id
    ).first()
    if not db_address:
        logger.warning(f"✗ العنوان غير موجود للتحديث - AddressID: {address_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="العنوان غير موجود")
    try:
        update_data = address_update.model_dump(exclude_unset=True)
        logger.debug(f"البيانات المرسلة للتحديث: {update_data}")
        if "ZoneID" in update_data:
            zone = db.query(DeliveryZone).filter(
                DeliveryZone.ZoneID == update_data["ZoneID"]
            ).first()
            if not zone:
                logger.warning(f"✗ المنطقة غير موجودة - ZoneID: {update_data['ZoneID']}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="المنطقة غير موجودة")
        logger.info(f"الحقول المراد تحديثها: {list(update_data.keys())}")
        for field, value in update_data.items():
            setattr(db_address, field, value)
        db.commit()
        db.refresh(db_address)
        logger.info(f"✓ تم تحديث العنوان بنجاح - AddressID: {address_id}")
        return db_address
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("✗ خطأ عند تحديث العنوان")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل التحديث")

# Delete an address
@address_router.delete("/delete/{user_id}/{address_id}")
def delete_address(
    user_id: uuid.UUID,
    address_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"محاولة حذف العنوان AddressID: {address_id}, UserID: {user_id}")
    db_address = db.query(Address).filter(
        Address.AddressID == address_id,
        Address.UserID == user_id
    ).first()
    if not db_address:
        logger.warning(f"✗ العنوان غير موجود للحذف - AddressID: {address_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="العنوان غير موجود")
    try:
        db.delete(db_address)
        db.commit()
        logger.info(f"✓ تم حذف العنوان بنجاح - AddressID: {address_id}")
        return {"message": "تم الحذف"}
    except Exception:
        db.rollback()
        logger.exception("✗ خطأ عند حذف العنوان")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل الحذف")


#=======================================
# DeliveryZone Routers
#=======================================

# Get all zones
@zone_router.get("/all_zones", response_model=List[ZoneResponse])
def get_all_zones(db: Session = Depends(get_db)):
    logger.info("عرض جميع المناطق")
    zones = db.query(DeliveryZone).order_by(DeliveryZone.ZoneID.asc()).all()
    logger.info(f"✓ تم جلب {len(zones)} منطقة")
    return zones

# Create a new zone
@zone_router.post("/create_zone", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
             zone: ZoneCreate,
             db: Session = Depends(get_db)):
    logger.info(f"محاولة إضافة منطقة جديدة: {zone.ZoneName}")
    logger.debug(f"بيانات المنطقة المستلمة: {zone.model_dump()}")
    try:
        db_zone = DeliveryZone(
            ZoneName=zone.ZoneName,
            DeliveryCost=zone.DeliveryCost
        )
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)
        logger.info(f"✓ تم إضافة المنطقة بنجاح - ZoneID: {db_zone.ZoneID}, Name: {db_zone.ZoneName}")
        return db_zone
    except IntegrityError as e:
        db.rollback()
        logger.error(f"✗ فشل إضافة المنطقة - الاسم مكرر: {zone.ZoneName}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اسم المنطقة موجود بالفعل"
        )
    except Exception:
        db.rollback()
        logger.exception("✗ خطأ عند إضافة المنطقة")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل إضافة المنطقة"
        )

# Get zone by ID
@zone_router.get("/zone/{zone_id}", response_model=ZoneResponse)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"طلب عرض المنطقة ZoneID: {zone_id}")
    zone = db.query(DeliveryZone).filter(DeliveryZone.ZoneID == zone_id).first()
    if not zone:
        logger.warning(f"✗ المنطقة غير موجودة - ZoneID: {zone_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المنطقة غير موجودة")
    logger.info(f"✓ تم جلب المنطقة - ZoneID: {zone_id}, Name: {zone.ZoneName}")
    return zone

# Update zone
@zone_router.put("/update_zone/{zone_id}", response_model=ZoneResponse)
def update_zone(
    zone_id: int,
    zone_update: ZoneUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"محاولة تحديث المنطقة ZoneID: {zone_id}")
    zone = db.query(DeliveryZone).filter(DeliveryZone.ZoneID == zone_id).first()
    if not zone:
        logger.warning(f"✗ المنطقة غير موجودة للتحديث - ZoneID: {zone_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المنطقة غير موجودة")
    try:
        update_data = zone_update.model_dump(exclude_unset=True)
        logger.debug(f"بيانات تحديث المنطقة: {update_data}")
        logger.info(f"الحقول المراد تحديثها: {list(update_data.keys())}")
        for field, value in update_data.items():
            setattr(zone, field, value)
        db.commit()
        db.refresh(zone)
        logger.info(f"✓ تم تحديث المنطقة بنجاح - ZoneID: {zone_id}")
        return zone
    except IntegrityError as e:
        db.rollback()
        logger.error(f"✗ فشل التحديث - الاسم مكرر: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اسم المنطقة موجود")
    except Exception:
        db.rollback()
        logger.exception("✗ خطأ عند تحديث المنطقة")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل التحديث")

# Delete zone
@zone_router.delete("/delete_zone/{zone_id}")
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"محاولة حذف المنطقة ZoneID: {zone_id}")
    zone = db.query(DeliveryZone).filter(DeliveryZone.ZoneID == zone_id).first()
    if not zone:
        logger.warning(f"✗ المنطقة غير موجودة للحذف - ZoneID: {zone_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المنطقة غير موجودة")
    try:
        zone_name = zone.ZoneName
        db.delete(zone)
        db.commit()
        logger.info(f"✓ تم حذف المنطقة بنجاح - ZoneID: {zone_id}, Name: {zone_name}")
        return {"message": "تم الحذف"}
    except Exception:
        db.rollback()
        logger.exception("✗ خطأ عند حذف المنطقة")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل الحذف")
