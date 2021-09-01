import abc
import re

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
        raise NotImplementedError

    def get_magic_id(self):
        return self.magic_id

    def parse_items_to_dict(self, item_set, columns={1: ''}):
        result = self.search_key_string_set(self.sheet, item_set, columns)
        self.sheet_str_to_number(result)
        return result

    @staticmethod
    def search_key_string_set(sheet: BeautifulSoup, search_set: set, columns):
        result = {}

        td = sheet.find_next('td')
        while search_set and td:
            zh_td_span = td.find('span', class_='zh')
            en_td_span = td.find('span', class_='en')
            for td_span in [zh_td_span, en_td_span]:
                if td_span:
                    span_item = td_span.string.lstrip()
                    if span_item in search_set:
                        span_item = re.split(' \\(|（', span_item)[0]
                        str_list = re.split(' |-', span_item.lower())
                        formatted_item_name = f'{str_list[0]}'
                        for this_str in str_list[1:]:
                            formatted_item_name += f'{this_str[0].upper()}{this_str[1:]}'

                        siblings_tds = td.find_next_siblings('td')
                        for idx, prefix in columns.items():
                            td_value = siblings_tds[idx - 1].find('ix:nonfraction').string
                            if prefix != '':
                                new_formatted = f'{formatted_item_name[0].upper()}{formatted_item_name[1:]}'
                                result[f'{prefix}{new_formatted}'] = td_value
                            else:
                                result[formatted_item_name] = td_value
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
