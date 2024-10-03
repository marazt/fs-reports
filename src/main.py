import json
import os
import subprocess
from datetime import datetime
from logging import Logger

from dtos import Config, Totals
from fakturoid_processor import FakturoidProcessor, FakturoidAuth
from logger import get_logger
from src.generator import generate_report, get_report_dir_name
from src.qr_payment import generate_qr_code

_logger: Logger = get_logger("fs-reports")


def main():
    with open("../config.json", encoding="utf-8") as config_file:
        config: Config = Config.from_dict(json.load(config_file))

    processor = FakturoidProcessor(FakturoidAuth(
        client_id=config.fakturoid.client_id,
        client_secret=config.fakturoid.client_secret,
        email=config.fakturoid.email,
        slug=config.fakturoid.slug
    ))

    totals: Totals = generate_report(processor, config, _logger)
    report_dir = get_report_dir_name(config)

    try:
        os.makedirs(report_dir)
    except FileExistsError:
        pass
    code_file_name = f"{report_dir}/qr_code_{config.period.year}_{config.period.month}"
    code_file_name_svg = f"{code_file_name}.svg"

    generate_qr_code(
        account=config.account.fs_tax_account,
        amount=totals.tax_diff,
        vs=config.account.vat_number,
        message=f"DPH {config.period.year}/{config.period.month:02}",
        due_date=datetime.now(),
        file_name=code_file_name_svg
    )

    subprocess.call(f"open {code_file_name_svg}", shell=True)


_logger.info("Now upload the report via https://adisspr.mfcr.cz/dpr/adis/idpr_epo/epo2/uvod/vstup_expert.faces")

if __name__ == "__main__":
    main()
