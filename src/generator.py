import os
from datetime import date
from logging import Logger

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
from typing import List

from src.dtos import Period, Invoice, Expense, Totals, Config
from src.processor import Processor


def generate_report(
        processor: Processor,
        config: Config,
        logger: Logger
) -> Totals:
    jinja_env = Environment(
        loader=FileSystemLoader("../templates"),
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
        return

    signed_on = date.today().strftime("%d.%m.%Y")

    _save_report(f"{config.output}/dphdp3_{period.year}_{period.month}m.xml",
                 jinja_env.get_template("dphdp3_template.xml").render(invoices=invoices,
                                                                      expenses=expenses,
                                                                      totals=totals,
                                                                      period=period,
                                                                      env=os.environ,
                                                                      signed_on=signed_on,
                                                                      user=config.user,
                                                                      account=config.account),
                 logger)

    _save_report(f"{config.output}/dphkh1_{period.year}_{period.month}m.xml",
                 jinja_env.get_template("dphkh1_template.xml").render(invoices=invoices,
                                                                      expenses=expenses,
                                                                      totals=totals,
                                                                      period=period,
                                                                      env=os.environ,
                                                                      signed_on=signed_on,
                                                                      user=config.user,
                                                                      account=config.account),
                 logger)

    return totals


def _print_info(logger: Logger, period: Period, invoices: List[Invoice], expenses: List[Expense], totals: Totals):
    logger.info(f"Report for period {period.year}-{period.month}.")
    logger.info(f"Invoices ({len(invoices)}):")
    for invoice in invoices:
        logger.info(
            f"\tInvoice {invoice.id}, {invoice.html_url} for {invoice.total} ({invoice.subtotal} base + {invoice.tax} tax).")

    logger.info(f"Expenses ({len(expenses)}):")
    for expense in expenses:
        logger.info(
            f"\tExpense {expense.id}, {expense.html_url} for {expense.total} ({expense.subtotal} base + {expense.tax} tax).")

    logger.info(f"Invoices total: {totals.total} ({totals.subtotal} base + {totals.tax} tax).")
    logger.info(f"Expenses total: {totals.supplier_total} ({totals.supplier_subtotal} base + {totals.supplier_tax} tax).")
    logger.info(f"Diff: {totals.total_diff}.")
    logger.info(f"Tax diff: {totals.tax_diff}.")


def _save_report(report_filename: str, data: str, logger: Logger):
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(data)
    logger.info(f"Report saved into file://{report_filename}.")
