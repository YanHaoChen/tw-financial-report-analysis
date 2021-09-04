import requests


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


if __name__ == '__main__':
    print(MonthlyRevenue(110, 8).content)