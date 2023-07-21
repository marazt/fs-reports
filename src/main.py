import json
from logging import Logger

from dtos import Config
from fakturoid_processor import FakturoidProcessor, FakturoidAuth
from logger import get_logger
from src.generator import generate_report

_logger: Logger = get_logger("fs-reports")


def main():
    with open("../config.json", encoding="utf-8") as config_file:
        config: Config = Config.from_dict(json.load(config_file))

    processor = FakturoidProcessor(FakturoidAuth(
        apikey=config.fakturoid.api_key,
        email=config.fakturoid.email,
        slug=config.fakturoid.slug
    ))

    generate_report(processor, config, _logger)

    _logger.info("Now upload the report via https://adisspr.mfcr.cz/dpr/adis/idpr_epo/epo2/uvod/vstup_expert.faces")


if __name__ == "__main__":
    main()
