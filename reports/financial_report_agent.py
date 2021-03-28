import requests
import logging

from bs4 import BeautifulSoup

from finance_td_parser import FinanceTDParser
from accounting_toolbox import accounting_numbers_to_ints


class FinancialReportAgent(object):
    def __new__(
        cls,
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
            soup = BeautifulSoup(resp.text, 'html.parser')

            check_status = soup.find('h4')
            # print(type(check_status))
            if check_status and check_status.string == '檔案不存在!':
                return None
            else:
                instance = super(FinancialReportAgent, cls).__new__(cls)
                instance.__dict__['soup'] = soup
                return instance
        except Exception as e:
            logging.exception(e)

    def __init__(
        self,
        company_id: str,
        year: int,
        season: int,
        report_type: str,
    ):
        self.company_id = company_id
        self.year = year
        self.season = season
        self.report_type = report_type
        self.balance_sheet = self.soup.find('table')

    def parser_balance_sheet(self, item_set: set):
        return self.parser_sheet_to_dict(self.balance_sheet, item_set)

    @staticmethod
    def parser_sheet_to_dict(sheet, item_set):
        td_parser = FinanceTDParser(sheet)
        result = td_parser.search_key_string_set(item_set)
        accounting_numbers_to_ints(result)
        return result
