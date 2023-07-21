import json
import os
import sys
from datetime import date
from logging import Logger

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

from dtos import Period, Config, Invoice, Expense, Totals
from fakturoid_processor import FakturoidProcessor, FakturoidAuth
from logger import get_logger
from processor import Processor

_logger: Logger = get_logger("fs-reports")


def main():
    with open("config.json", encoding="utf-8") as config_file:
        config: Config = Config.from_dict(json.load(config_file))

    processor = FakturoidProcessor(FakturoidAuth(
        apikey=config.fakturoid.api_key,
        email=config.fakturoid.email,
        slug=config.fakturoid.slug
    ))

    _generate_report(processor, config, _logger)

    _logger.info("Now upload the report via https://adisspr.mfcr.cz/dpr/adis/idpr_epo/epo2/uvod/vstup_expert.faces")


def _print_info(logger: Logger, period: Period, invoices: list[Invoice], expenses: list[Expense], totals: Totals):
    logger.info(f"Report for period {period.year}-{period.month}.")
    logger.info(f"Invoices ({len(invoices)}):")
    for invoice in invoices:
        logger.info(
            f"\tInvoice {invoice.id}, {invoice.html_url} for {invoice.total} ({invoice.subtotal} + {invoice.tax}).")

    logger.info(f"Expenses ({len(expenses)}):")
    for expense in expenses:
        logger.info(
            f"\tExpense {expense.id}, {expense.html_url} for {expense.total} ({expense.subtotal} + {expense.tax}).")

    logger.info(f"Invoices total: {totals.total} ({totals.subtotal} + {totals.tax}).")
    logger.info(f"Expenses total: {totals.supplier_total} ({totals.supplier_subtotal} + {totals.supplier_tax}).")
    logger.info(f"Diff: {totals.total_diff}.")
    logger.info(f"Tax diff: {totals.tax_diff}.")


def _generate_report(
        processor: Processor,
        config: Config,
        logger: Logger
):
    jinja_env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["xml"]),
        undefined=StrictUndefined
    )
    period = config.period
    invoices = processor.process_invoices(period)
    expenses = processor.process_expenses(period)
    totals = processor.generate_totals(invoices, expenses)

    _print_info(logger, period, invoices, expenses, totals)

    if len(invoices) == 0 and len(expenses) == 0:
        logger.info("No invoices nor expenses found, quitting.")
        sys.exit(1)

    template = jinja_env.get_template("dphdp3_template.xml")
    signed_on = date.today().strftime("%d.%m.%Y")

    with open(f"./reports/dphdp3_{period.year}_{period.month}m.xml", "w", encoding="utf-8") as f:
        f.write(template.render(invoices=invoices,
                                expenses=expenses,
                                totals=totals,
                                period=period,
                                env=os.environ,
                                signed_on=signed_on,
                                user=config.user,
                                account=config.account))

    template = jinja_env.get_template("dphkh1_template.xml")
    with open(f"./reports/dphkh1_{period.year}_{period.month}m.xml", "w", encoding="utf-8") as f:
        f.write(template.render(invoices=invoices,
                                expenses=expenses,
                                totals=totals,
                                period=period,
                                env=os.environ,
                                signed_on=signed_on,
                                user=config.user,
                                account=config.account))


if __name__ == "__main__":
    main()
