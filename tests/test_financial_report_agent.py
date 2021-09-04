from reports.financial_report_agent import FinancialReportAgent
import unittest
from unittest import mock

RESOURCE_PATH = './tests/resources'


class FinancialReportAgentTestCase(unittest.TestCase):

    def mocked_requests_get(*args, **kwargs):
        class MockResponse(object):
            def __init__(self, text):
                self.encoding = 'big5'
                self.text = text

        if args[0] == (f'https://mops.twse.com.tw/server-java/t164sb01?step=1&'
                       f'CO_ID=6666&'
                       f'SYEAR=2021&'
                       f'SSEASON=4&'
                       f'REPORT_ID=C'):

            with open(f'{RESOURCE_PATH}/mock_financial_report_success_example.html', 'r', encoding='big5') as f:
                success_html = f.read()
            return MockResponse(text=success_html)
        elif args[0] == (f'https://mops.twse.com.tw/server-java/t164sb01?step=1&'
                         f'CO_ID=6666&'
                         f'SYEAR=2021&'
                         f'SSEASON=5&'
                         f'REPORT_ID=C'):

            with open(f'{RESOURCE_PATH}/mock_financial_report_fail_example.html', 'r', encoding='big5') as f:
                fail_html = f.read()
            return MockResponse(text=fail_html)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_financial_report_success(self, mock_get):
        agent = FinancialReportAgent(company_id='6666',
                                     year=2021,
                                     season=4,
                                     report_type='C')

        search_balance_sheet_set_us = {'Total assets'}
        search_balance_sheet_set_tw = {'資產總計'}
        us_result = agent.balance_sheet.parse_items_to_dict(search_balance_sheet_set_us, {2: ''})
        tw_result = agent.balance_sheet.parse_items_to_dict(search_balance_sheet_set_tw, {2: ''})

        self.assertIsNotNone(agent)
        self.assertIn(mock.call(f'https://mops.twse.com.tw/server-java/t164sb01?step=1&'
                                f'CO_ID=6666&'
                                f'SYEAR=2021&'
                                f'SSEASON=4&'
                                f'REPORT_ID=C'), mock_get.call_args_list)

        # test parsing unit
        self.assertEqual(agent.balance_sheet.dollar_unit, 1000)
        # test parsing column
        self.assertEqual(us_result['totalAssets'], tw_result['資產總計'])
        # test parsing result
        self.assertEqual(us_result['totalAssets'], 5564612)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_financial_report_when_file_is_not_exist_fail(self, mock_get):
        agent = FinancialReportAgent(company_id='6666',
                                     year=2021,
                                     season=5,
                                     report_type='C')
        self.assertIsNone(agent)
        self.assertIn(mock.call(f'https://mops.twse.com.tw/server-java/t164sb01?step=1&'
                                f'CO_ID=6666&'
                                f'SYEAR=2021&'
                                f'SSEASON=5&'
                                f'REPORT_ID=C'), mock_get.call_args_list)


if __name__ == '__main__':
    RESOURCE_PATH = './resources'
    unittest.main()
