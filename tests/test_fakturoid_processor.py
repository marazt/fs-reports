import filecmp
import json
import os
from http import HTTPStatus
from logging import Logger

import pytest

from src.dtos import Config
from src.fakturoid_processor import FakturoidProcessor, FakturoidAuth
from src.generator import generate_report
from src.logger import get_logger

_logger: Logger = get_logger("tests")


@pytest.fixture()
def mocked_invoices():
    with open("./test_data/invoices.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture()
def mocked_expenses():
    with open("./test_data/expenses.json", encoding="utf-8") as f:
        return json.load(f)


def test_should_generate_reports(mocker, mocked_invoices, mocked_expenses):
    processor = FakturoidProcessor(FakturoidAuth(
        apikey="apikey",
        email="user@example.org",
        slug="user"
    ))

    mocked_responses = [mocker.Mock(), mocker.Mock()]
    mocked_responses[0].json.return_value = mocked_invoices
    mocked_responses[0].status_code = HTTPStatus.OK
    mocked_responses[1].json.return_value = mocked_expenses
    mocked_responses[1].status_code = HTTPStatus.OK

    mocker.patch("src.fakturoid_processor.requests.get", side_effect=mocked_responses)

    with open("./test_data/config1.json", encoding="utf-8") as config_file:
        config: Config = Config.from_dict(json.load(config_file))

    generate_report(processor, config, _logger)

    assert filecmp.cmp("./test_reports/dphdp3_2023_6m.xml", "./test_data/dphdp3_2023_6m.xml")
    assert filecmp.cmp("./test_reports/dphkh1_2023_6m.xml", "./test_data/dphkh1_2023_6m.xml")


def test_should_not_generate_reports(mocker, mocked_invoices, mocked_expenses):
    processor = FakturoidProcessor(FakturoidAuth(
        apikey="apikey",
        email="user@example.org",
        slug="user"
    ))

    mocked_responses = [mocker.Mock(), mocker.Mock()]
    mocked_responses[0].json.return_value = mocked_invoices
    mocked_responses[0].status_code = HTTPStatus.OK
    mocked_responses[1].json.return_value = mocked_expenses
    mocked_responses[1].status_code = HTTPStatus.OK

    mocker.patch("src.fakturoid_processor.requests.get", side_effect=mocked_responses)

    with open("./test_data/config2.json", encoding="utf-8") as config_file:
        config: Config = Config.from_dict(json.load(config_file))

    generate_report(processor, config, _logger)

    assert not os.path.exists("./test_reports/dphdp3_2023_4m.xml")
    assert not os.path.exists("./test_reports/dphkh1_2023_4m.xml")
