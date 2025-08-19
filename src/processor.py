from typing import List

from dtos import Invoice, Expense, Period, Totals
from src.dtos import Config


class Processor:
    """
    Base Processor.
    """

    def __init__(self):
        pass

    def process_invoices(self, period: Period) -> List[Invoice]:
        """
        Invoice processing.
        :param period:
        :return:
        """

    def process_expenses(self, period: Period) -> List[Expense]:
        """
        Expenses processing
        :param period:
        :return:
        """

    def process_expenses_from_file(self, config: Config) -> List[Expense]:
        """
        Expenses processing
        :param config:
        :return:
        """

    @staticmethod
    def generate_totals(invoices: List[Invoice], expenses: List[Expense]) -> Totals:
        """
        Totals stats generator.
        :param invoices:
        :param expenses:
        :return:
        """
        total = sum(i.total for i in invoices)
        subtotal = sum(i.subtotal for i in invoices)
        tax = sum(i.tax for i in invoices)
        supplier_total = sum(i.total for i in expenses)
        supplier_subtotal = sum(i.subtotal for i in expenses)
        supplier_tax = sum(i.tax for i in expenses)

        return Totals(
            total=total,
            subtotal=subtotal,
            tax=tax,
            supplier_total=supplier_total,
            supplier_subtotal=supplier_subtotal,
            supplier_tax=supplier_tax,
            total_diff=total - supplier_total,
            tax_diff=tax - supplier_tax
        )
