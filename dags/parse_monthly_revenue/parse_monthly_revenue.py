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

def init_dag(start_date, schedule_interval='30 12 12 * *'):
    args = {
        'owner': 'sean',
    }
    dag = DAG(
        dag_id='parse_monthly_revenue',
        default_args=args,
        max_active_runs=2,
        concurrency=2,
        schedule_interval=schedule_interval,
        start_date=start_date,
    )

    @EnvSetting.append_project_to_path
    def parse_monthly_revenue(**context):
        from airflow.providers.mongo.hooks.mongo import MongoHook

        from reports.monthly_revenue.monthly_revenue import MonthlyRevenue
        from reports.monthly_revenue.monthly_revenue import MonthlyRevenueCollection
        from toolbox.date_tool import DateTool

        mongo_hook = MongoHook(conn_id='stock_mongo')
        stock_db = mongo_hook.get_conn().stock
        mr_collection_struct = MonthlyRevenueCollection()
        monthly_revenue_collection = mr_collection_struct.bind_db(stock_db)

        next_execution_date = context['next_ds']
        target_year, target_month, _ = map(int, next_execution_date.split('-'))
        logging.info(f'parsing {target_year}/{target_month} monthly revenue.')

        mr_results = MonthlyRevenue(tw_year=DateTool.to_tw_year(target_year), month=target_month).monthly_revenues

        for result in mr_results:
            monthly_revenue_collection.update_one(
                filter=mr_collection_struct.get_unique_fields(result),
                update={'$set': result},
                upsert=True
            )

        logging.info(f'{target_year}/{target_month} monthly revenue is finished!')

    parse_monthly_revenue_task = PythonOperator(
        task_id='parse_monthly_revenue',
        provide_context=True,
        python_callable=parse_monthly_revenue,
        depends_on_past=True,
        retries=3,
        retry_delay=timedelta(seconds=30),
        dag=dag
    )

    parse_monthly_revenue_task

    return dag


parse_monthly_revenue_dag = init_dag(start_date=datetime(year=2018, month=12, day=1))
