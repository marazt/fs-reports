import os
from datetime import date
from logging import Logger
from typing import List, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

from src.dtos import Period, Invoice, Expense, Totals, Config
from src.processor import Processor


def generate_report(
        processor: Processor,
        config: Config,
        logger: Logger
) -> Totals | None:
    jinja_env = Environment(
        loader=FileSystemLoader("../templates"),
        autoescape=select_autoescape(["xml"]),
        undefined=StrictUndefined
    )
    period = config.period
    invoices = processor.process_invoices(period)

    valid_client_vat_numbers: Dict[str, str] = {vat.number: vat.name for vat in config.valid_client_vat_numbers}
    valid_supplier_vat_numbers: Dict[str, str] = {vat.number: vat.name for vat in config.valid_supplier_vat_numbers}

    for invoice in invoices:
        if invoice.client_vat_number not in valid_client_vat_numbers.keys():
            raise Exception(
                f"Client with VAT number {invoice.client_vat_number} not found in valid client VAT numbers.")

    expenses = processor.process_expenses(period)

    for expense in expenses:
        if expense.supplier_vat_number not in valid_supplier_vat_numbers.keys():
            raise Exception(
                f"Supplier with VAT number {expense.supplier_vat_number} not found in valid supplier VAT numbers.")

    totals = processor.generate_totals(invoices, expenses)

    _print_info(logger, period, invoices, expenses, totals, valid_client_vat_numbers, valid_supplier_vat_numbers)

    if len(invoices) == 0 and len(expenses) == 0:
        logger.info("No invoices nor expenses found, quitting.")
        return

    signed_on = date.today().strftime("%d.%m.%Y")
    report_dir = f"{config.output}/{period.year}_{period.month}"
    _save_report(report_dir, f"dphdp3_{period.year}_{period.month}m.xml",
                 jinja_env.get_template("dphdp3_template.xml").render(invoices=invoices,
                                                                      expenses=expenses,
                                                                      totals=totals,
                                                                      period=period,
                                                                      env=os.environ,
                                                                      signed_on=signed_on,
                                                                      user=config.user,
                                                                      account=config.account),
                 logger)

    _save_report(report_dir, f"dphkh1_{period.year}_{period.month}m.xml",
                 jinja_env.get_template("dphkh1_template.xml").render(invoices=invoices,
                                                                      expenses=expenses,
                                                                      totals=totals,
                                                                      period=period,
                                                                      env=os.environ,
                                                                      signed_on=signed_on,
                                                                      user=config.user,
                                                                      account=config.account),
                 logger)

    logger.info(f"Reports saved into file://{report_dir}.")
    logger.info(f"Control report: https://adisspr.mfcr.cz/pmd/epo/novy/DPH_KH1.")
    logger.info(f"VAT: https://adisspr.mfcr.cz/pmd/epo/novy/DPH_DP3.")

    return totals


def _print_info(logger: Logger, period: Period, invoices: List[Invoice], expenses: List[Expense], totals: Totals,
                valid_vat_numbers: Dict[str, str], valid_supplier_vat_numbers: Dict[str, str]):
    logger.info(f"Report for period {period.year}-{period.month}.")
    logger.info(f"Invoices ({len(invoices)}):")
    for invoice in invoices:
        logger.info(
            f"\tInvoice {invoice.id} from client {valid_vat_numbers[invoice.client_vat_number]}, {invoice.html_url} for {invoice.total} ({invoice.subtotal} base + {invoice.tax} tax).")

    logger.info(f"Expenses ({len(expenses)}):")
    for expense in expenses:
        logger.info(
            f"\tExpense {expense.id} from supplier {valid_supplier_vat_numbers[expense.supplier_vat_number]}, {expense.html_url} for {expense.total} ({expense.subtotal} base + {expense.tax} tax).")

    logger.info(f"Invoices total: {totals.total} ({totals.subtotal} base + {totals.tax} tax).")
    logger.info(
        f"Expenses total: {totals.supplier_total} ({totals.supplier_subtotal} base + {totals.supplier_tax} tax).")
    logger.info(f"Diff: {totals.total_diff}.")
    logger.info(f"Tax diff: {totals.tax_diff}.")


def _save_report(report_dir: str, report_filename: str, data: str, logger: Logger):
    try:
        os.makedirs(report_dir)
    except FileExistsError:
        pass
    full_name = f"{report_dir}/{report_filename}"
    with open(full_name, "w", encoding="utf-8") as f:
        f.write(data)
    logger.info(f"Report saved into file://{full_name}.")
