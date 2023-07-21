import math
from dataclasses import dataclass
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

from dtos import Period, Invoice, Expense
from processor import Processor


@dataclass
class FakturoidAuth:
    apikey: str
    email: str
    slug: str


class FakturoidProcessor(Processor):
    """
    Fakturoid data processor.
    """

    def __init__(self, auth: FakturoidAuth):
        super().__init__()
        self._auth = auth

    def process_invoices(self, period: Period) -> list[Invoice]:
        data = self._get_all_invoices_for(period, self._auth)
        return FakturoidProcessor.transform_invoices(data)

    def process_expenses(self, period: Period) -> list[Expense]:
        data = self._get_all_expenses_for(period, self._auth)
        return FakturoidProcessor.transform_expenses(data)

    def _get_all_invoices_for(self, period: Period, auth: FakturoidAuth) -> list[dict]:
        url = f"https://app.fakturoid.cz/api/v2/accounts/{auth.slug}/invoices.json"
        r = requests.get(url, auth=HTTPBasicAuth(auth.email, auth.apikey), timeout=2)
        invoices_all = r.json()

        invoices = list(filter(lambda i: self._is_in_period(i, period), invoices_all))
        return invoices

    def _get_all_expenses_for(self, period: Period, auth: FakturoidAuth) -> list[dict]:
        url = f"https://app.fakturoid.cz/api/v2/accounts/{auth.slug}/expenses.json"
        r = requests.get(url, auth=HTTPBasicAuth(auth.email, auth.apikey), timeout=2)
        expenses_all = r.json()

        expenses = list(filter(lambda i: self._is_in_period(i, period), expenses_all))
        return expenses

    def _is_in_period(self, invoice: dict, period: Period):
        taxable_fulfillment_due = datetime.strptime(invoice["taxable_fulfillment_due"], "%Y-%m-%d")
        return taxable_fulfillment_due.year == period.year and taxable_fulfillment_due.month == period.month

    @staticmethod
    def transform_expenses(expenses: list[dict]) -> list[Expense]:
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
    def transform_invoices(invoices: list[dict]) -> list[Invoice]:
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
