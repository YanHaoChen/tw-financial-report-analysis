import requests

from db_bridges.mongo_bridge.collection_structure import CollectionStructure
from toolbox.date_tool import DateTool


class YahooDailyTransactionsCollection(CollectionStructure):
    def set_name(self):
        return 'yahooDailyTransactions'

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
            'high': 0.0,
            'low': 0.0,
            'volume': 0,
            'close': 0.0,
            'open': 0.0,
        }


class YahooDailyTransaction(object):

    def __init__(self, stock: str, year: int, month: int, day: int):
        self.document = None
        start_period = DateTool.date_to_timestamp(
            year=year,
            month=month,
            day=day
        )
        end_period = DateTool.date_to_timestamp(
            year=year,
            month=month,
            day=day,
            end=True
        )
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'
        }

        resp = requests.get(
            url=f'https://query1.finance.yahoo.com/v8/finance/chart/{stock}',
            params={
                'period1': start_period,
                'period2': end_period,
                'interval': '1d',
                'events': 'history',
            },
            headers=headers
        )
        resp.encoding = 'utf8'
        json_resp = resp.json()
        this_day_data = json_resp['chart']['result'][0]['indicators']['quote'][0]
        if this_day_data:
            self.document = YahooDailyTransactionsCollection().document_operator(
                stockCode=stock,
                year=year,
                month=month,
                day=day,
                intDate=year*10000+month*100+day,
                high=this_day_data['high'][0],
                low=this_day_data['low'][0],
                volume=this_day_data['volume'][0],
                close=this_day_data['close'][0],
                open=this_day_data['open'][0]
            )


def main():
    # ^GSPC
    new_stock = YahooDailyTransaction('^GSPC', 2022, 1, 2)
    print(new_stock.document)
    pass


if __name__ == '__main__':
    main()