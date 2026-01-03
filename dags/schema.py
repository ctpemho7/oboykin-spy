from pydantic import BaseModel, Field, model_validator
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

    roll_id: int
    url: str

    class Config:
        from_attributes = True

    @staticmethod
    def get_target_fields():
        return [
            "roll_id",
            "url",
        ]
    
    def to_row(self):
        return [  
            self.roll_id,
            self.url,
        ]
    


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
    uri: str
    
    rapor: Optional[str] = None # Раппорт, см
    pattern: Optional[str] = None  # Рисунок
    moisture_resistance: Optional[str] = None
    production_technology: Optional[str] = None
    light_fastness: Optional[str] = None
    glue_application: Optional[str] = None

    # options запускается до того, как Pydantic начнет проверять типы
    @model_validator(mode='before')
    @classmethod
    def extract_options(cls, data: dict):
        # берет словарь options, 
        # достаем оттуда значения из поля value 
        # и подкладываем их в основной словарь

        options = data.get("options", {})
        
        # Маппинг: ключ в модели -> ключ в options
        mapping = {
            "rapor": "rapor",
            "pattern": "room",
            "moisture_resistance": "wp-wet",
            "production_technology": "wp-tech",
            "light_fastness": "wp-light",
            "glue_application": "wp-kleyhow"
        }
        
        for model_key, json_key in mapping.items():
            opt_data = options.get(json_key)
            if opt_data and isinstance(opt_data, dict):
                data[model_key] = opt_data.get("value")
            elif opt_data: # на случай если там сразу строка
                data[model_key] = opt_data
               
        return data

    vendor: Vendor
    parent: Parent

    @property
    def collection(self) -> str:
        """Получить название коллекции из parent"""
        return self.parent.pagetitle
        
    class Config:
        from_attributes = True
        populate_by_name = True  # разрешить использование alias

    @staticmethod
    def get_target_fields():
        return [
            "id",
            "vendor_id",
            "collection",
            "uri",
            "height",
            "width",
            "weight",
            "article",
            "base",
            "cover",
            "rapor",
            "pattern",
            "moisture_resistance",
            "production_technology",
            "light_fastness",
            "glue_application",
        ]

    def to_row(self):
        return [
            self.id,
            self.vendor.id,
            self.collection,
            self.uri,
            self.height,
            self.width,
            self.weight,
            self.article,
            self.base,
            self.cover,
            self.rapor,
            self.pattern,
            self.moisture_resistance,
            self.production_technology,
            self.light_fastness,
            self.glue_application,
        ]

class Fact(BaseModel):
    """Таблица фактов (наличие в магазине)"""
    id: int
    roll_id: int
    shop_id: int
    price: float
    available: int

    class Config:
        from_attributes = True

    @staticmethod
    def get_target_fields():
        return [
            "roll_id",
            "shop_id",
            "price",
            "available",
        ]

    def to_row(self):
        return [
            self.roll_id,
            self.shop_id,
            self.price,
            self.available
        ]
