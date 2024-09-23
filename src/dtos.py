from dataclasses import dataclass
from datetime import datetime
from typing import Any, List


@dataclass
class Invoice:
    """
    Invoice.
    """
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
    """
    Expense.
    """
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
    """
    Totals.
    """
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
    """
    Account.
    """
    vat_number: int
    ufo_code: int
    prac_ufo: int
    id_data_box: str
    fs_tax_account: str

    @staticmethod
    def from_dict(obj: Any) -> "Account":
        vat_number = int(obj.get("vat_number"))
        ufo_code = int(obj.get("ufo_code"))
        prac_ufo = int(obj.get("prac_ufo"))
        id_data_box = str(obj.get("id_data_box"))
        fs_tax_account = str(obj.get("fs_tax_account"))
        return Account(vat_number, ufo_code, prac_ufo, id_data_box, fs_tax_account)


@dataclass
class Address:
    """
    Address.
    """
    city: str
    street_name: str
    street_number: int
    street_orientation_number: str
    zip_code: int
    country: str

    @staticmethod
    def from_dict(obj: Any) -> "Address":
        city = str(obj.get("city"))
        street_name = str(obj.get("street_name"))
        street_number = int(obj.get("street_number"))
        street_orientation_number = str(obj.get("street_orientation_number"))
        zip_code = int(obj.get("zip_code"))
        country = str(obj.get("country"))
        return Address(city, street_name, street_number, street_orientation_number, zip_code, country)


@dataclass
class Fakturoid:
    """
    Fakturoid.
    """
    slug: str
    client_id: str
    client_secret: str
    email: str

    @staticmethod
    def from_dict(obj: Any) -> "Fakturoid":
        slug = str(obj.get("slug"))
        client_id = str(obj.get("client_id"))
        client_secret = str(obj.get("client_secret"))
        email = str(obj.get("email"))
        return Fakturoid(slug, client_id, client_secret, email)


@dataclass
class Period:
    """
    Period.
    """
    year: int
    month: int

    @staticmethod
    def from_dict(obj: Any) -> "Period":
        year = int(obj.get("year"))
        month = int(obj.get("month"))
        return Period(year, month)


@dataclass
class User:
    """
    User.
    """
    first_name: str
    last_name: str
    title: str
    phone_number: str
    email: str
    address: Address

    @staticmethod
    def from_dict(obj: Any) -> "User":
        first_name = str(obj.get("first_name"))
        last_name = str(obj.get("last_name"))
        title = str(obj.get("title"))
        phone_number = str(obj.get("phone_number"))
        email = str(obj.get("email"))
        address = Address.from_dict(obj.get("address"))
        return User(first_name, last_name, title, phone_number, email, address)


@dataclass
class ValidClientVatNumber:
    name: str
    number: str

    @staticmethod
    def from_dict(obj: Any) -> 'ValidClientVatNumber':
        _name = str(obj.get("name"))
        _number = str(obj.get("number"))
        return ValidClientVatNumber(_name, _number)


@dataclass
class ValidSupplierVatNumber:
    name: str
    number: str

    @staticmethod
    def from_dict(obj: Any) -> 'ValidSupplierVatNumber':
        _name = str(obj.get("name"))
        _number = str(obj.get("number"))
        return ValidSupplierVatNumber(_name, _number)


@dataclass
class Config:
    """
    Config.
    """
    period: Period
    fakturoid: Fakturoid
    user: User
    account: Account
    output: str
    valid_client_vat_numbers: List[ValidClientVatNumber]
    valid_supplier_vat_numbers: List[ValidSupplierVatNumber]

    @staticmethod
    def from_dict(obj: Any) -> "Config":
        period = Period.from_dict(obj.get("period"))
        fakturoid = Fakturoid.from_dict(obj.get("fakturoid"))
        user = User.from_dict(obj.get("user"))
        account = Account.from_dict(obj.get("account"))
        output = str(obj.get("output"))
        valid_client_vat_numbers = [ValidClientVatNumber.from_dict(y) for y in obj.get("valid_client_vat_numbers")]
        valid_suppliers_vat_numbers = [ValidSupplierVatNumber.from_dict(y) for y in
                                       obj.get("valid_supplier_vat_numbers")]
        return Config(period, fakturoid, user, account, output, valid_client_vat_numbers, valid_suppliers_vat_numbers)
