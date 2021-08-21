import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from functools import wraps


class EnvSetting(object):
    AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
    PROJECT_HOME = f'{AIRFLOW_HOME}/dags/tw-financial-report-analysis'

    @staticmethod
    def append_project_to_path(f):
        @wraps(f)
        def insert_path(*args, **kwds):
            sys.path.insert(0, EnvSetting.PROJECT_HOME)
            return f(*args, **kwds)

        return insert_path


# 2633 A

def init_dag(dag_id, stock_code, report_type, start_date, schedule_interval='0 0 27 * *'):
    args = {
        'owner': 'sean',
    }
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        max_active_runs=1,
        concurrency=1,
        schedule_interval=schedule_interval,
        start_date=start_date,
    )

    @EnvSetting.append_project_to_path
    def check_report_in_mongo(code, **context):
        from airflow.providers.mongo.hooks.mongo import MongoHook

        from toolbox.date_tool import DateTool

        mongo_hook = MongoHook(conn_id='stock_mongo')
        stock_db = mongo_hook.get_conn().stock
        execution_date = context['ds']
        year, month, day = map(int, execution_date.split('-'))
        season, season_year = DateTool.date_to_ex_season_and_year(year, month)
        upload_key = {
            'stock_code': code,
            'year': season_year,
            'season': season,
            'year_and_season': season_year * 10 + season
        }
        has_report = stock_db.financialReports.find_one(upload_key)
        if has_report:
            return 'report_already_in_mongo'
        else:
            return 'checkout_report_released'

    check_report_in_mongo_task = BranchPythonOperator(
        task_id='check_report_in_mongo',
        python_callable=check_report_in_mongo,
        op_kwargs={
            'code': stock_code,
        },
        provide_context=True,
        dag=dag,
    )

    report_already_in_mongo_task = DummyOperator(
        task_id='report_already_in_mongo',
        dag=dag
    )

    @EnvSetting.append_project_to_path
    def checkout_report_released(code, r_type, **context):
        import requests
        from datetime import datetime
        import pytz

        from airflow.providers.mongo.hooks.mongo import MongoHook
        from bs4 import BeautifulSoup

        from toolbox.date_tool import DateTool

        mongo_hook = MongoHook(conn_id='stock_mongo')
        stock_db = mongo_hook.get_conn().stock
        execution_date = context['ds']
        year, month, day = map(int, execution_date.split('-'))
        season, season_year = DateTool.date_to_ex_season_and_year(year, month)
        tw_year = DateTool.to_tw_year(season_year)

        resp = requests.get(
            f'https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&'
            f'co_id={code}&'
            f'year={tw_year}&'
            f'seamon={season}&'
            f'mtype=A')
        resp.encoding = 'big5'
        soup = BeautifulSoup(resp.text, 'html.parser')

        if soup.h4 and soup.h4.text == '查無所需資料':
            return 'the_report_is_not_exist'

        report_date_str = soup.center.table.table.find(attrs={'align': 'cetern'}).text
        report_tw_year, *others = report_date_str.split('/')
        report_year = DateTool.tw_year_to_year(int(report_tw_year))
        tw_date_str = '/'.join([str(report_year)] + others)
        report_date = datetime.strptime(tw_date_str, '%Y/%m/%d %H:%M:%S')
        timezone = pytz.timezone('Asia/Taipei')
        report_date = timezone.localize(report_date)
        upload_data = {
            'stock_code': code,
            'year': season_year,
            'season': season,
            'year_and_season': season_year * 10 + season,
            'uploaded_date': report_date
        }
        stock_db.financialReports.insert(upload_data)

        return 'load_report_to_mongo'

    checkout_report_released_task = BranchPythonOperator(
        task_id='checkout_report_released',
        python_callable=checkout_report_released,
        op_kwargs={
            'code': stock_code,
            'r_type': report_type
        },
        provide_context=True,
        trigger_rule='none_failed_or_skipped',
        dag=dag,
    )

    the_report_is_not_exist_task = DummyOperator(
        task_id='the_report_is_not_exist',
        dag=dag
    )

    @EnvSetting.append_project_to_path
    def load_report_to_mongo_by_stock_code(code, r_type, **context):
        from reports.financial_report_agent import FinancialReportAgent
        from toolbox.date_tool import DateTool
        from airflow.providers.mongo.hooks.mongo import MongoHook
        mongo_hook = MongoHook(conn_id='stock_mongo')
        stock_db = mongo_hook.get_conn().stock
        execution_date = context['ds']
        year, month, day = map(int, execution_date.split('-'))
        season, season_year = DateTool.date_to_ex_season_and_year(year, month)
        fn_report_agent = FinancialReportAgent(code, season_year, season, r_type)
        upload_key = {
            'stock_code': code,
            'year': season_year,
            'season': season,
            'year_and_season': season_year * 10 + season
        }
        upload_data = {}
        if not fn_report_agent:
            return 'cant_get_the_report'

        ''' Balance Sheet '''
        search_balance_sheet_set = {
            'Total assets',
            'Total current assets',
            'Total non-current assets',
            'Total liabilities',
            'Total current liabilities',
            'Total non-current liabilities',
            'Total equity',
            'Ordinary share'
        }
        balance_sheet_res = fn_report_agent.balance_sheet.parse_items_to_dict(search_balance_sheet_set)
        upload_data.update(balance_sheet_res)
        # record the unit of Balance Sheet
        upload_data.update(
            {
                'balanceSheetUnit': fn_report_agent.balance_sheet.dollar_unit
            }
        )

        ''' Comprehensive Income Sheet '''
        search_comprehensive_income_sheet_set = {
            'Total operating revenue',
            'Total operating costs',
            'Total comprehensive income',
            'Total basic earnings per share',
        }
        income_res = fn_report_agent.comprehensive_income_sheet.parse_items_to_dict(
            search_comprehensive_income_sheet_set
        )
        upload_data.update(income_res)

        # Record the unit of Comprehensive Income Sheet
        upload_data.update(
            {
                'comprehensiveIncomeSheetUnit': fn_report_agent.comprehensive_income_sheet.dollar_unit
            }
        )

        ''' compute ROA, ROE and Book Value Per Share '''
        roa = upload_data.get('totalComprehensiveIncome', 0) / upload_data.get('totalAssets', 1)
        roe = upload_data.get('totalComprehensiveIncome', 0) / upload_data.get('totalEquity', 1)
        assets = upload_data.get('totalAssets', 0)
        liabilities = upload_data.get('totalLiabilities', 0)
        net_worth = assets - liabilities
        shares = (upload_data.get('ordinaryShare', 0) / 10)
        book_value_per_share = net_worth / shares if shares > 0 else 0

        upload_data.update(
            {
                'roa': round(roa, 4),
                'roe': round(roe, 4),
                'netWorth': net_worth,
                'shares': shares,
                'bookValuePerShare': round(book_value_per_share, 4),
            }
        )

        ''' concat key and data '''

        stock_db.financialReports.update(
            upload_key,
            {
                "$set": upload_data
            },
            upsert=True
        )

        return 'done'

    load_report_to_mongo_task = BranchPythonOperator(
        task_id='load_report_to_mongo',
        python_callable=load_report_to_mongo_by_stock_code,
        op_kwargs={
            'code': stock_code,
            'r_type': report_type
        },
        trigger_rule='none_failed_or_skipped',
        provide_context=True,
        dag=dag,
    )

    cant_get_the_report_task = DummyOperator(
        task_id='cant_get_the_report',
        dag=dag
    )

    done_task = DummyOperator(
        task_id='done',
        dag=dag
    )
    check_report_in_mongo_task >> [report_already_in_mongo_task, checkout_report_released_task]
    checkout_report_released_task >> [the_report_is_not_exist_task, load_report_to_mongo_task]
    load_report_to_mongo_task >> [cant_get_the_report_task, done_task]

    return dag


stock_2633 = init_dag(f'stock_2633', stock_code=2633, report_type='A', start_date=datetime(year=2019, month=4, day=1))
stock_5283 = init_dag(f'stock_5283', stock_code=5283, report_type='C', start_date=datetime(year=2019, month=4, day=1))
