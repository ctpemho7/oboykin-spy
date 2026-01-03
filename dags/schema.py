from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Vendor(BaseModel):
    """Производитель"""

    id: int
    name: str
    country: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class Shop(BaseModel):
    """Магазин"""

    id: int
    name: str
    address: str

    class Config:
        from_attributes = True


class Asset(BaseModel):
    """Фото"""

    id: int
    roll_id: int
    url: str

    class Config:
        from_attributes = True


class Parent(BaseModel):
    """Родительская категория (коллекция)"""
    id: int
    pagetitle: str
    uri: str

    class Config:
        from_attributes = True


class Roll(BaseModel):
    """Рулон"""

    id: int
    height: float
    width: float
    weight: float
    article: str
    base: str  # Основа
    cover: str  # Покрытие
    rapor: int = Field(default=None, alias="rapor")  # Раппорт, см
    pattern: Optional[str] = Field(default=None, alias="room")  # Рисунок
    
    # options
    moisture_resistance: Optional[str] = Field(default=None, alias="wp-wet")  # Влагостойкость
    production_technology: Optional[str] = Field(default=None, alias="wp-tech")  # Технология производства
    light_fastness: Optional[str] = Field(default=None, alias="wp-light")  # Светостойкость
    glue_application: Optional[str] = Field(default=None, alias="wp-kleyhow")  # Нанесение клея
    
    vendor: Vendor
    parent: Parent

    @property
    def collection(self) -> str:
        """Получить название коллекции из parent"""
        return self.parent.pagetitle
    

    @field_validator('color', mode='before')
    @classmethod
    def parse_colors(cls, v):
        """Преобразует список строк в список объектов Color"""
        if isinstance(v, list):
            return [
                Color(id=idx, name=color) if isinstance(color, str) else color
                for idx, color in enumerate(v, start=1)
            ]
        return v

    class Config:
        from_attributes = True
        populate_by_name = True  # разрешить использование alias


class Fact(BaseModel):
    """Таблица фактов (наличие в магазине)"""
    id: int
    roll_id: int
    shop_id: int
    price: float
    available: int

    class Config:
        from_attributes = True

