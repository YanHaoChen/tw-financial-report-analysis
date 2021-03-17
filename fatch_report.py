import requests

from bs4 import BeautifulSoup

from accounting_toolbox import accounting_numbers_to_ints
from reports.financial_report_agent import FinancialReportAgent


def run():
    fn_report_agent = FinancialReportAgent(2605, 2020, 3, "C")

    resp = requests.get(
        f'{"https://mops.twse.com.tw/server-java/t164sb01?"}'
        f'{"step=1&CO_ID=2605&SYEAR=2020&SSEASON=2&REPORT_ID=C"}')

    """
    1XXX:資產總計, Total assets
    2XXX:負債總計
    3XXX:權益總額
    """
    search_set = {'資產總計', '負債總計', 'Total assets'}
    result = fn_report_agent.parser_balance_sheet(search_set)
    print(result)


if __name__ == '__main__':
    run()
