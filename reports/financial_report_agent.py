import requests
import logging

from bs4 import BeautifulSoup

from finance_td_parser import FinanceTDParser
from accounting_toolbox import accounting_numbers_to_ints


class FinancialReportAgent:
    def __init__(
        self,
        company_id: str,
        year: int,
        season: int,
        report_type: str
    ):
        try:
            resp = requests.get(
                f'{"https://mops.twse.com.tw/server-java/t164sb01?step=1&"}'
                f'CO_ID={company_id}&'
                f'SYEAR={year}&'
                f'SSEASON={season}&'
                f'REPORT_ID={report_type}')
            resp.encoding = 'big5'
            self.soup = BeautifulSoup(resp.text, 'html.parser')
            self.balance_sheet = self.soup.find('table')

        except Exception as e:
            logging.exception(e)

    def parser_balance_sheet(self, item_set: set):
        return self.parser_sheet_to_dict(self.balance_sheet, item_set)

    @staticmethod
    def parser_sheet_to_dict(sheet, item_set):
        td_parser = FinanceTDParser(sheet)
        result = td_parser.search_key_string_set(item_set)
        accounting_numbers_to_ints(result)
        return result
