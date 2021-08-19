# tw-financial-report-analysis

遲早都要分析財報，怎麼不一開始就自己分析？

### 已完成項目
* 財報定期抓取
    * 資產負載表
    * 綜合損益表
* 指標
    * ROE
    * ROA
    * 每股淨值（bookValuePerShare）
    * EPS（totalBasicEarningsPerShare）

### 環境安裝

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

### 建立 mongo 使用者

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
### 建立 Mongo Connection
在建立之前，先讓 Airflow Webserver 新增 Mongo 的 Connection Type。
```
docker exec -it airflow_airflow-webserver_1 pip3 install apache-airflow-providers-mongo==2.0.0

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

### 把檔案導入 `dags`
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

### 初始化專案

在 Airflow Webserver 上，開啟 `setup_parse_financial_report` DAG。把所需 package 在 Worker 上安裝好。

### 開始拉報表囉！

在 Airflow Webserver 上，開啟 `stock_2633`。檢查是否有資料導入 Mongo：
```bash
docker exec -it test_airflow_mongo_1 bash
mongosh -u airflower -p money stock
stock> db.financialReports.find({})
[
  {
    _id: ObjectId("611e8ab916925b41b58f44cc"),
    totalCurrentAssets: 21002761,
    totalNonCurrentAssets: 408287953,
    totalAssets: 429290714,
    totalCurrentLiabilities: 5496779,
    totalNonCurrentLiabilities: 352093178,
    totalLiabilities: 357589957,
    ordinaryShare: 56282930,
    totalEquity: 71700757,
    balanceSheetUnit: 1000,
    totalOperatingRevenue: 11762190,
    totalOperatingCosts: 6227537,
    totalComprehensiveIncome: 2287744,
    totalBasicEarningsPerShare: 0.41,
    comprehensiveIncomeSheetUnit: 1000,
    roa: 0.0053,
    roe: 0.0319,
    netWorth: 71700757,
    shares: 5628293,
    bookValuePerShare: 12.7393,
    stock_code: 2633,
    year: 2019,
    season: 1,
    year_and_season: 20191
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
>