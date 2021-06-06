import abc
from bs4 import BeautifulSoup


class Sheet(abc.ABC):
    def __init__(self):
        self.magic_id = ""
        self.dollar_unit = 0
        self.sheet = None

    def set_dollar_unit(self, dollar_unit):
        self.dollar_unit = dollar_unit

    @abc.abstractmethod
    def set_magic_id(self):
        pass

    def get_magic_id(self):
        return self.magic_id

    def parse_items_to_dict(self, item_set):
        result = self.search_key_string_set(self.sheet, item_set)
        self.sheet_str_to_number(result)
        return result

    @staticmethod
    def search_key_string_set(sheet: BeautifulSoup, search_set: set):
        result = {}

        td = sheet.find_next('td')
        while search_set and td:
            zh_td_span = td.find('span', class_='zh')
            en_td_span = td.find('span', class_='en')
            for td_span in [zh_td_span, en_td_span]:
                if td_span:
                    span_item = td_span.string.lstrip()
                    if span_item in search_set:
                        td_value = td.find_next('td').find('ix:nonfraction').string
                        result[span_item] = td_value
                        search_set.remove(span_item)
                        break

            td = td.find_next('td')

        return result

    @staticmethod
    def sheet_str_to_number(result_dict: dict):
        for key, acc_number in result_dict.items():
            number = acc_number.replace(",", "")
            if '(' in number:
                result_dict[key] = float(number[1:-1]) * -1.0
            else:
                result_dict[key] = float(number)
