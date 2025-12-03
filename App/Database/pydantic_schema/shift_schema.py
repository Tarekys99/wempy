from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date, time

#======================================
# Shifts Schemas - مبسط
#======================================

class ShiftStart(BaseModel):
    """ما يدخله الكاشير فقط"""
    Shift_Number: str = Field(..., description= "رقم الوردية")

class ShiftResponse(BaseModel):
    """الاستجابة"""
    ShiftID: int
    Shift_Date: date
    Shift_Number: str
    Start_Time: time
    End_Time: time | None
    IsActive: bool
    
    model_config = ConfigDict(from_attributes=True)