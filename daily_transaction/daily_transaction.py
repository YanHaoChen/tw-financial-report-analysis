import requests

from db_bridges.mongo_bridge.collection_structure import CollectionStructure
from toolbox.date_tool import DateTool

class DailyTransactionsCollection(CollectionStructure):
    def set_name(self):
            return 'dailyTransactions'

    def set_unique_fields(self):
        return {
            'stockCode': str,
            'year': int,
            'month': int,
            'day': int,
            'intDate': int,
        }

    def set_data_fields(self):
        return {
            'tradeVolume': 0,
            'amount': 0,
            'openingPrice': 0.0,
            'highestPrice': 0.0,
            'lowestPrice': 0.0,
            'closingPrice': 0.0,
            'closingDiff': 0.0,
            'transaction': 0,
        }


class DailyTransactionsInMonth(object):
    @staticmethod
    def remove_comma_to_int(with_comma: str) -> int:
        return int(with_comma.replace(',', ''))

    @staticmethod
    def remove_comma_to_float(with_comma: str) -> float:
        return float(with_comma.replace(',', ''))

    @staticmethod
    def distinguish_sign_to_float(with_sign: str) -> float:
        if with_sign[0] == '-':
            return -1.0 * float(with_sign[1:])
        else:
            return float(with_sign[1:])

    def __init__(self, stock: str, year: int, month: int):
        self.documents = list()

        resp = requests.get(
            url='https://www.twse.com.tw/exchangeReport/STOCK_DAY',
            params={
                'response': 'json',
                'date': f'{year}{month:0>2}01',
                'stockNo': stock,
            }
        )
        resp.encoding = 'utf8'
        json_resp = resp.json()

        for daily_info in json_resp['data']:
            got_tw_year, got_month, got_day = map(int, daily_info[0].split('/'))
            got_year = DateTool.tw_year_to_year(got_tw_year)
            self.documents.append(
                DailyTransactionsCollection().document_operator(
                    stockCode=stock,
                    year=got_year,
                    month=got_month,
                    day=got_day,
                    intDate=got_year * 10000 + got_month * 100 + got_day,
                    tradeVolume=self.__class__.remove_comma_to_int(daily_info[1]),
                    amount=self.__class__.remove_comma_to_int(daily_info[2]),
                    openingPrice=self.__class__.remove_comma_to_float(daily_info[3]),
                    highestPrice=self.__class__.remove_comma_to_float(daily_info[4]),
                    lowestPrice=self.__class__.remove_comma_to_float(daily_info[5]),
                    closingPrice=self.__class__.remove_comma_to_float(daily_info[6]),
                    closingDiff=self.__class__.distinguish_sign_to_float(daily_info[7]),
                    transaction=self.__class__.remove_comma_to_int(daily_info[8]),
                )
            )


def main():
    new_stock = DailyTransactionsInMonth('0050', 2021, 1)
    print(new_stock.documents)
    pass


if __name__ == '__main__':
    main()