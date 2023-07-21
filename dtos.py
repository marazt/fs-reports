from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Invoice:
    due_on: datetime
    id: str
    issued_on: datetime
    note: str
    number: str
    order_number: str
    client_registration_number: str
    subtotal: float
    tax: float
    taxable_fulfillment_due: datetime
    total: float
    html_url: str
    variable_symbol: str
    client_vat_number: str
    vat_price_mode: str


@dataclass
class Expense:
    document_type: str
    due_on: datetime
    id: str
    issued_on: datetime
    original_number: str
    number: str
    supplier_registration_number: str
    supplier_vat_number: str
    subtotal: float
    tax: float
    taxable_fulfillment_due: datetime
    total: float
    html_url: str
    variable_symbol: str
    vat_price_mode: str


@dataclass
class Totals:
    total: float
    subtotal: float
    tax: float
    supplier_total: float
    supplier_subtotal: float
    supplier_tax: float
    total_diff: float
    tax_diff: float


@dataclass
class Account:
    vat_number: int
    ufo_code: int
    prac_ufo: int
    id_data_box: str

    @staticmethod
    def from_dict(obj: Any) -> 'Account':
        _vat_number = int(obj.get("vat_number"))
        _ufo_code = int(obj.get("ufo_code"))
        _prac_ufo = int(obj.get("prac_ufo"))
        _id_data_box = str(obj.get("id_data_box"))
        return Account(_vat_number, _ufo_code, _prac_ufo, _id_data_box)


@dataclass
class Address:
    city: str
    street_name: str
    street_number: int
    street_orientation_number: str
    zip_code: int
    country: str

    @staticmethod
    def from_dict(obj: Any) -> 'Address':
        _city = str(obj.get("city"))
        _street_name = str(obj.get("street_name"))
        _street_number = int(obj.get("street_number"))
        _street_orientation_number = str(obj.get("street_orientation_number"))
        _zip_code = int(obj.get("zip_code"))
        _country = str(obj.get("country"))
        return Address(_city, _street_name, _street_number, _street_orientation_number, _zip_code, _country)


@dataclass
class Fakturoid:
    slug: str
    api_key: str
    email: str

    @staticmethod
    def from_dict(obj: Any) -> 'Fakturoid':
        _slug = str(obj.get("slug"))
        _api_key = str(obj.get("api_key"))
        _email = str(obj.get("email"))
        return Fakturoid(_slug, _api_key, _email)


@dataclass
class Period:
    year: int
    month: int

    @staticmethod
    def from_dict(obj: Any) -> 'Period':
        _year = int(obj.get("year"))
        _month = int(obj.get("month"))
        return Period(_year, _month)


@dataclass
class User:
    first_name: str
    last_name: str
    title: str
    phone_number: str
    email: str
    address: Address

    @staticmethod
    def from_dict(obj: Any) -> 'User':
        _first_name = str(obj.get("first_name"))
        _last_name = str(obj.get("last_name"))
        _title = str(obj.get("title"))
        _phone_number = str(obj.get("phone_number"))
        _email = str(obj.get("email"))
        _address = Address.from_dict(obj.get("address"))
        return User(_first_name, _last_name, _title, _phone_number, _email, _address)


@dataclass
class Config:
    period: Period
    fakturoid: Fakturoid
    user: User
    account: Account

    @staticmethod
    def from_dict(obj: Any) -> 'Config':
        _period = Period.from_dict(obj.get("period"))
        _fakturoid = Fakturoid.from_dict(obj.get("fakturoid"))
        _user = User.from_dict(obj.get("user"))
        _account = Account.from_dict(obj.get("account"))
        return Config(_period, _fakturoid, _user, _account)
