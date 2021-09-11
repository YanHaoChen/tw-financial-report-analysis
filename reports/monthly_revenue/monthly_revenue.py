import requests

from db_bridges.mongo_bridge.collection_structure import CollectionStructure
from toolbox.date_tool import DateTool

class MonthlyRevenueCollection(CollectionStructure):
    def set_name(self):
        return 'monthlyRevenues'

    def set_unique_fields(self):
        return {
            'stockCode': str,
            'year': int,
            'month': int,
        }

    def set_data_fields(self):
        return {
            'company': 'unknown',
            'industrialClass': 'unknown',
            'theMonthlyRevenue': 0.0,
            'exMonthlyRevenue': 0.0,
            'exYearTheMonthlyRevenue': 0.0,
            'mom': 0.0,
            'yoy': 0.0,
            'cumTheMonthlyRevenue': 0.0,
            'cumExYearTheMonthlyRevenue': 0.0,
            'cmocm': 0.0,
            'note': '-'
        }


class MonthlyRevenue(object):
    def __init__(self, tw_year, month):
        resp = requests.post(
            url='https://mops.twse.com.tw/server-java/FileDownLoad',
            data={
                'step': '9',
                'functionName': 'show_file',
                'filePath': '/home/html/nas/t21/sii/',
                'fileName': f't21sc03_{tw_year}_{month}.csv'
            }
        )
        resp.encoding = 'utf8'
        self.content = resp.text

        self.monthly_revenues = list()

        def str_to_float(this_str: str):
            try:
                return float(this_str)
            except ValueError:
                return 0.0

        for company in resp.text.split('\r\n')[1:-1]:
            items = company.replace('"', '').split(',')
            tw_year, month = tuple(map(int, items[1].split('/')))

            self.monthly_revenues.append(
                MonthlyRevenueCollection().document_operator(
                    stockCode=items[2],
                    year=DateTool.tw_year_to_year(tw_year),
                    month=month,
                    company=items[3],
                    industrialClass=items[4],
                    theMonthlyRevenue=str_to_float(items[5]),
                    exMonthlyRevenue=str_to_float(items[6]),
                    exYearTheMonthlyRevenue=str_to_float(items[7]),
                    mom=str_to_float(items[8]),
                    yoy=str_to_float(items[9]),
                    cumTheMonthlyRevenue=str_to_float(items[10]),
                    cumExYearTheMonthlyRevenue=str_to_float(items[11]),
                    cmocm=str_to_float(items[12]),
                    note=items[13]
                )
            )


if __name__ == '__main__':
    for document in MonthlyRevenue(110, 8).monthly_revenues:
        print(document)