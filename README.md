# tw-financial-report-analysis

遲早都要分析財報，怎麼不一開始就自己分析？

## 已完成項目
* 財報定期抓取
    * 資產負載表
    * 綜合損益表
* 指標
    * ROE
    * ROA
    * 每股淨值（bookValuePerShare）
    * EPS（totalBasicEarningsPerShare）
    * 財報公佈日期（publishedDate）

## 環境安裝

在家目錄下安裝：
```bash
cd ~
mkdir airflow
cd airflow
curl -LfO 'https://github.com/YanHaoChen/tw-financial-report-analysis/raw/main/for_setup_airlfow/docker-compose.yaml'
mkdir ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
docker-compose up airflow-init
docker-compose up -d
```

## 建立 mongo 使用者

```bash
docker exec -it airflow_mongo_1 bash
mongosh -u root -p example

> use stock
> db.createUser(
	{
		user:"airflower",
		pwd: "money",
		roles:[
			{ role: "readWrite", db: "stock" }
		]
	}
)
> exit
exit
```
## 建立 Mongo Connection
在建立之前，先讓 Airflow Webserver 新增 Mongo 的 Connection Type。
```
docker exec -it airflow_airflow-webserver_1 pip3 install apache-airflow-providers-mongo==1.0.0

# 刷新 Airflow Web
docker-compose restart
```
接下來，連進 Airflow Webserver `127.0.0.1:8080`。點選 Admin -> Connections -> 點選加號(Add a new record)。再照以下項目填寫：

* Conn Id: stock_mongo
* Conn Type: MongoDB
* Host: stock_mongo
* Schema: stock
* Login: airflower
* Password: money
* Port: 27017

> Airflow Webserver 預設帳號密碼都是: airflow

## 把檔案導入 `dags`
在把專案放進 `dags` 前，先把 `airflowignore.template` 放進去。

```bash
cd ./dags
curl -LfO 'https://github.com/YanHaoChen/tw-financial-report-analysis/raw/main/for_setup_airlfow/airflowignore.template'
mv airflowignore.template .airflowignore
```
現在把可以把專案拉下來囉！
```bash
git clone https://github.com/YanHaoChen/tw-financial-report-analysis.git
```
現在回到 Airflow Webserver， 等 3~5 分鐘就可以看到這個專案裡的拉報表的 DAG 囉！

## 初始化專案

在 Airflow Webserver 上，開啟 `setup_parse_financial_report` DAG。把所需 package 在 Worker 上安裝好。

## 開始拉報表囉！

在 Airflow Webserver 上，開啟 `stock_2633`。檢查是否有資料導入 Mongo：
```bash
docker exec -it airflow_mongo_1 bash
mongosh -u airflower -p money stock
stock> db.financialReports.find({})
[
  {
    _id: ObjectId("6121166ea9629beb059291a4"),
    stockCode: 2633,
    year: 2019,
    season: 1,
    yearAndSeason: 20191,
    publishedDate: ISODate("2019-05-10T08:36:04.000Z"),
    balanceSheetUnit: 1000,
    bookValuePerShare: 12.7393,
    comprehensiveIncomeSheetUnit: 1000,
    netWorth: 71700757,
    ordinaryShare: 56282930,
    roa: 0.0053,
    roe: 0.0319,
    shares: 5628293,
    totalAssets: 429290714,
    totalBasicEarningsPerShare: 0.41,
    totalComprehensiveIncome: 2287744,
    totalCurrentAssets: 21002761,
    totalCurrentLiabilities: 5496779,
    totalEquity: 71700757,
    totalLiabilities: 357589957,
    totalNonCurrentAssets: 408287953,
    totalNonCurrentLiabilities: 352093178,
    totalOperatingCosts: 6227537,
    totalOperatingRevenue: 11762190
  }
]
```


> 如果發生:
>```
>from reports.financial_report_agent import FinancialReportAgent
> ModuleNotFoundError: No module named 'reports'
>```
> 重啟 airflow 即可：
>```
>docker-compose restart
>```

## 新增其他公司財報
1. 先到以下網址，查詢欲新增的公司。

    [公開資訊觀測站-資產負債表查詢](https://mops.twse.com.tw/mops/web/t164sb03)

2. 取得欲新增公司的財報類型。

    點選 「投資人若需了解更詳細資訊可至XBRL資訊平台或電子書查詢」中的`XBRL資訊平台`。透過 URL 就可以知道財報的種類。
    ```
    # 以 1234 為例，財報類型為: REPORT_ID=C
    https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID=1234&SYEAR=2021&SSEASON=2&REPORT_ID=C
    ```
3. 新增對應 DAG。
    至檔案 `dags/parse_financial_report/parse_financial_report.py` 的最下方，加入以下程式碼即可：
    ```python
    ...
    stock_2633 = init_dag('stock_2633', stock_code=2633, report_type='A', start_date=datetime(year=2019, month=4, day=1))
    stock_5283 = init_dag('stock_5283', stock_code=5283, report_type='C', start_date=datetime(year=2019, month=4, day=1))
    # new
    stock_1234 = init_dag('stock_1234', stock_code=1234, report_type='C', start_date=datetime(year=2019, month=4, day=1))
    # 每日執行則:
    stock_1234 = init_dag(
        'stock_1234',
        stock_code=1234,
        report_type='C',
        start_date=datetime(year=2019, month=4, day=1),
        schedule_interval='0 0 * * *'
   )
    ```
   > 目前規劃抓取 2019 年第一季以後的財報格式，所以 `start_date` 需大於 2019-04-01，才能正確抓取。
