import logging
import sys
from datetime import datetime
from datetime import timedelta
from functools import wraps

from airflow.settings import AIRFLOW_HOME
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator


class EnvSetting(object):
    PROJECT_HOME = f'{AIRFLOW_HOME}/dags/tw-financial-report-analysis'

    @staticmethod
    def append_project_to_path(f):
        @wraps(f)
        def insert_path(*args, **kwds):
            sys.path.insert(0, EnvSetting.PROJECT_HOME)
            return f(*args, **kwds)

        return insert_path


def init_dag(stock_code, start_date, schedule_interval='30 12 * * *'):
    args = {
        'owner': 'sean',
    }
    dag = DAG(
        dag_id=f'crawl_{stock_code}_yahoo_daily_transaction',
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

        from daily_transaction.yahoo_daily_transaction import YahooDailyTransaction
        from daily_transaction.yahoo_daily_transaction import YahooDailyTransactionsCollection

        mongo_hook = MongoHook(conn_id='stock_mongo')
        stock_db = mongo_hook.get_conn().stock
        ydt_collection_struct = YahooDailyTransactionsCollection()
        yahoo_daily_transaction_collection = ydt_collection_struct.bind_db(stock_db)

        execution_date = context['ds']
        target_year, target_month, target_day = map(int, execution_date.split('-'))
        logging.info(f'parsing daily stock of {target_year}/{target_month}/{target_day}.')

        ydt_result = YahooDailyTransaction(
            stock=stock_code,
            year=target_year,
            month=target_month,
            day=target_day
        ).document
        logging.info(f'data: {ydt_result}')

        if ydt_result:
            yahoo_daily_transaction_collection.update_one(
                filter=ydt_collection_struct.get_unique_fields(ydt_result),
                update={'$set': ydt_result},
                upsert=True
            )
            logging.info(f'sleep 10 second.')
            sleep(10)
            logging.info(f'{target_year}/{target_month}/{target_day} daily transaction is finished!')
            return 'done'
        else:
            return 'no_data'

    parse_daily_transaction_task = BranchPythonOperator(
        task_id='crawl_daily_transaction',
        provide_context=True,
        python_callable=crawl_daily_transaction,
        depends_on_past=True,
        retries=3,
        retry_delay=timedelta(seconds=30),
        dag=dag
    )

    no_data_task = DummyOperator(
        task_id='no_data',
        dag=dag
    )

    done_task = DummyOperator(
        task_id='done',
        dag=dag
    )

    parse_daily_transaction_task >> [no_data_task, done_task]

    return dag


parse_0050_transaction_dag = init_dag(stock_code='0050.TW', start_date=datetime(year=2018, month=12, day=1))
