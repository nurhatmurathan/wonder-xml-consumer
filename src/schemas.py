from typing import List, Optional
from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    merchant_id: str
    store_name: str


class DeleteOfferSchema(BaseModel):
    merchant_id: str
    sku: str


class DisablePickupSchema(BaseModel):
    merchant_id: str
    store_id: str


class OfferScuIdsSchema(BaseModel):
    sku: str


class EnablePickupSchema(BaseModel):
    merchant_id: str
    store_id: str
    offers_sku: List[OfferScuIdsSchema]


class OfferAvailabilitySchema(BaseModel):
    storeId: str
    available: bool


class OfferCityPriceSchema(BaseModel):
    cityId: str
    price: int


class OffersSchema(BaseModel):
    sku: str
    model: str
    brand: Optional[str] = None
    availabilities: List[OfferAvailabilitySchema]
    city_prices: Optional[List[OfferCityPriceSchema]] = None
    price: Optional[int] = None


class AddNewOffersSchema(BaseModel):
    merchant_id: str
    offers: List[OffersSchema]
