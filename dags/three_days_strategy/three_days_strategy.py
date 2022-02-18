import logging
import sys
from datetime import datetime
from datetime import timedelta
from functools import wraps

from airflow.settings import AIRFLOW_HOME
from airflow import DAG
from airflow.operators.python import PythonOperator
from functools import wraps


class EnvSetting(object):
    PROJECT_HOME = f'{AIRFLOW_HOME}/dags/tw-financial-report-analysis'

    @staticmethod
    def append_project_to_path(f):
        @wraps(f)
        def insert_path(*args, **kwds):
            sys.path.insert(0, EnvSetting.PROJECT_HOME)
            return f(*args, **kwds)

        return insert_path


# 2633 A

def init_dag(stock_code, start_date, schedule_interval='30 12 1 * *'):
    args = {
        'owner': 'sean',
    }
    dag = DAG(
        dag_id=f'crawl_{stock_code}_daily_transaction',
        default_args=args,
        max_active_runs=2,
        concurrency=2,
        schedule_interval=schedule_interval,
        start_date=start_date,
        tags=['stock'],
    )

    @EnvSetting.append_project_to_path
    def crawl_daily_transaction(**context):
        from time import sleep

        from airflow.providers.mongo.hooks.mongo import MongoHook

        from daily_transaction.daily_transaction import DailyTransactionsInMonth
        from daily_transaction.daily_transaction import DailyTransactionsCollection

        mongo_hook = MongoHook(conn_id='stock_mongo')
        stock_db = mongo_hook.get_conn().stock
        dt_collection_struct = DailyTransactionsCollection()
        daily_transaction_collection = dt_collection_struct.bind_db(stock_db)

        execution_date = context['ds']
        target_year, target_month, _ = map(int, execution_date.split('-'))
        logging.info(f'parsing daily stock of {target_year}/{target_month}.')

        dt_results = DailyTransactionsInMonth(stock=stock_code, year=target_year, month=target_month).documents

        for result in dt_results:
            daily_transaction_collection.update_one(
                filter=dt_collection_struct.get_unique_fields(result),
                update={'$set': result},
                upsert=True
            )

        logging.info(f'sleep 5 second.')
        sleep(5)
        logging.info(f'{target_year}/{target_month} daily transaction is finished!')

    parse_daily_transaction_task = PythonOperator(
        task_id='crawl_daily_transaction',
        provide_context=True,
        python_callable=crawl_daily_transaction,
        depends_on_past=True,
        retries=3,
        retry_delay=timedelta(seconds=30),
        dag=dag
    )

    parse_daily_transaction_task

    return dag


parse_0050_transaction_dag = init_dag(stock_code='0050', start_date=datetime(year=2018, month=12, day=1))
