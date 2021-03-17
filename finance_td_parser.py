from bs4 import BeautifulSoup


class FinanceTDParser:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def search_key_string_set(self, search_set: set):
        result = {}

        td = self.soup.find_next('td')
        while search_set and td:
            zh_td_span = td.find_next('span', class_='zh')
            en_td_span = td.find_next('span', class_='en')
            for td_span in [zh_td_span, en_td_span]:
                if td_span:
                    span_item = td_span.string.lstrip()
                    if span_item in search_set:
                        td_value = td.find_next('td').find(
                            'ix:nonfraction').string
                        result[span_item] = td_value
                        search_set.remove(span_item)

            td = td.find_next('td')

        return result
