import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from requests.auth import _basic_auth_str

from dtos import Period, Invoice, Expense, Config
from processor import Processor
from src.generator import get_report_dir_name


# from requests.auth import basic_auth_str


@dataclass
class FakturoidAuth:
    client_id: str
    client_secret: str
    email: str
    slug: str


class FakturoidProcessor(Processor):
    """
    Fakturoid data processor.
    """

    def __init__(self, auth: FakturoidAuth):
        super().__init__()
        self._auth = auth
        self._base_url = "https://app.fakturoid.cz/api/v3"
        self._accounts_url = f"{self._base_url}/accounts"
        self._token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def process_invoices(self, period: Period) -> List[Invoice]:
        data = self._get_all_invoices_for(period, self._auth)
        return FakturoidProcessor.transform_invoices(data)

    def process_expenses(self, period: Period) -> List[Expense]:
        data = self._get_all_expenses_for(period, self._auth)
        return FakturoidProcessor.transform_expenses(data)

    def process_expenses_from_file(self, config: Config) -> List[Expense]:
        try:
            with open(f"{get_report_dir_name(config)}/expenses.json", "r") as f:
                data: list[dict] = json.load(f)
                return FakturoidProcessor.transform_expenses_from_file(data)
        except Exception as ex:
            print(f"Error reading expenses from file: {ex}")
            return []

    def _get_url(self, auth: FakturoidAuth, suffix: str):
        return f"{self._accounts_url}/{auth.slug}/{suffix}"

    def _get_token(self, auth: FakturoidAuth):
        now = datetime.now()
        if self._token is not None and self._expires_at is not None and self._expires_at > now:
            return self._token

        url = f"{self._base_url}/oauth/token"
        r = requests.post(
            url,
            headers={
                "User-Agent": f"fsreport ({auth.email})",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": _basic_auth_str(auth.client_id, auth.client_secret)
            },
            json={"grant_type": "client_credentials"},
            timeout=2
        )
        data = r.json()
        self._token = data["access_token"]
        self._expires_at = now + timedelta(seconds=data["expires_in"])
        return self._token

    def _create_headers_with_token(self):
        return {
            "Authorization": f"Bearer {self._get_token(self._auth)}",
        }

    def _get_all_invoices_for(self, period: Period, auth: FakturoidAuth) -> List[dict]:
        r = requests.get(self._get_url(auth, "invoices.json"), headers=self._create_headers_with_token(), timeout=2)
        invoices_all = r.json()

        invoices = list(filter(lambda i: self._is_in_period(i, period), invoices_all))
        return invoices

    def _get_all_expenses_for(self, period: Period, auth: FakturoidAuth) -> List[dict]:
        r = requests.get(self._get_url(auth, "expenses.json"), headers=self._create_headers_with_token(), timeout=2)
        expenses_all = r.json()

        expenses = list(filter(lambda i: self._is_in_period(i, period), expenses_all))
        return expenses

    def _is_in_period(self, invoice: dict, period: Period):
        taxable_fulfillment_due = datetime.strptime(invoice["taxable_fulfillment_due"], "%Y-%m-%d")
        return taxable_fulfillment_due.year == period.year and taxable_fulfillment_due.month == period.month

    @staticmethod
    def transform_expenses(expenses: List[dict]) -> List[Expense]:
        return [
            Expense(
                document_type=expense["document_type"],
                due_on=datetime.strptime(expense["due_on"], "%Y-%m-%d"),
                id=expense["id"],
                issued_on=datetime.strptime(expense["issued_on"], "%Y-%m-%d"),
                original_number=expense["original_number"],
                number=expense["number"],
                supplier_registration_number=expense["supplier_registration_no"],
                supplier_vat_number=expense["supplier_vat_no"],
                subtotal=math.ceil(float(expense["subtotal"])),
                tax=math.ceil(float(expense["total"])) - math.ceil(float(expense["subtotal"])),
                taxable_fulfillment_due=datetime.strptime(expense["taxable_fulfillment_due"], "%Y-%m-%d"),
                total=math.ceil(float(expense["total"])),
                html_url=expense["html_url"],
                variable_symbol=expense["variable_symbol"],
                vat_price_mode=expense["vat_price_mode"],
            ) for expense in expenses
        ]

    @staticmethod
    def transform_expenses_from_file(expenses: List[dict]) -> List[Expense]:
        return [
            Expense(
                document_type="",
                due_on=datetime.strptime(expense["due_on"], "%Y-%m-%d"),
                id=expense["supplier_registration_number"] + "-" + expense["variable_symbol"],
                issued_on=datetime.strptime(expense["issued_on"], "%Y-%m-%d"),
                original_number=expense["original_number"],
                number="",
                supplier_registration_number=expense["supplier_registration_number"],
                supplier_vat_number=expense["supplier_vat_number"],
                subtotal=math.ceil(float(expense["subtotal"])),
                tax=math.ceil(float(expense["total"])) - math.ceil(float(expense["subtotal"])),
                taxable_fulfillment_due=datetime.strptime(expense["taxable_fulfillment_due"], "%Y-%m-%d"),
                total=math.ceil(float(expense["total"])),
                html_url="",
                variable_symbol=expense["variable_symbol"],
                vat_price_mode="",
            ) for expense in expenses
        ]

    @staticmethod
    def transform_invoices(invoices: List[dict]) -> List[Invoice]:
        return [
            Invoice(
                due_on=datetime.strptime(invoice["due_on"], "%Y-%m-%d"),
                id=invoice["id"],
                issued_on=datetime.strptime(invoice["issued_on"], "%Y-%m-%d"),
                note=invoice["note"],
                number=invoice["number"],
                order_number=invoice["order_number"],
                client_registration_number=invoice["client_registration_no"],
                subtotal=math.ceil(float(invoice["subtotal"])),
                tax=math.ceil(float(invoice["total"])) - math.ceil(float(invoice["subtotal"])),
                taxable_fulfillment_due=datetime.strptime(invoice["taxable_fulfillment_due"], "%Y-%m-%d"),
                total=math.ceil(float(invoice["total"])),
                html_url=invoice["html_url"],
                variable_symbol=invoice["variable_symbol"],
                client_vat_number=invoice["client_vat_no"],
                vat_price_mode=invoice["vat_price_mode"],
            ) for invoice in invoices
        ]
