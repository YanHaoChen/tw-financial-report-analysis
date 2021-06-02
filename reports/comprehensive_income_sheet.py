from reports.sheet import Sheet
from bs4 import BeautifulSoup


class ComprehensiveIncomeSheet(Sheet):
    def __init__(self, sheet: BeautifulSoup):
        self.magic_id = 'StatementOfComprehensiveIncome'
        self.sheet = sheet
        self.dollar_unit = 0