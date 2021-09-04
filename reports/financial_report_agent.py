import requests
import logging

from bs4 import BeautifulSoup

from reports.sheet import Sheet
from reports.balance_sheet import BalanceSheet
from reports.comprehensive_income_sheet import ComprehensiveIncomeSheet


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
                f'https://mops.twse.com.tw/server-java/t164sb01?step=1&'
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
        self.balance_sheet = BalanceSheet(self.soup.find('table'))
        self.parse_sheet_unit(self.balance_sheet, self.soup)
        self.comprehensive_income_sheet = ComprehensiveIncomeSheet(self.balance_sheet.sheet.find_next_sibling('table'))
        self.parse_sheet_unit(self.comprehensive_income_sheet, self.soup)

    @staticmethod
    def parse_sheet_unit(sheet: Sheet, report_html: BeautifulSoup):
        unit_string = report_html.find(
            'div', id=sheet.get_magic_id()
        ).find_next(
            'div', 'rptidx'
        ).find(
            'span', 'en'
        ).string

        if 'thousands' in unit_string:
            sheet.set_dollar_unit(1000)
        else:
            logging.warning(f'Unkown unit: {unit_string}')

        return sheet


if __name__ == '__main__':
    # search_comprehensive_income_set = {
    #     'Total operating revenue',
    #     'Total operating costs',
    #     'Total basic earnings per share'
    # }
    fn_report_agent = FinancialReportAgent("2605", 2020, 3, "C")
    search_balance_sheet_set = {
        'Total assets',
        'Total current assets',
        'Total non-current assets',
        'Total liabilities',
        'Total current liabilities',
        'Total non-current liabilities',
        'Total equity'
    }
    balance_sheet_res = fn_report_agent.balance_sheet.parse_items_to_dict(search_balance_sheet_set)
    print(balance_sheet_res)
    search_comprehensive_income_sheet_set = {
        'Total operating revenue',
        'Total operating costs',
        'Total basic earnings per share'
    }
    income_res = fn_report_agent.comprehensive_income_sheet.parse_items_to_dict(search_comprehensive_income_sheet_set)
    print(income_res)
