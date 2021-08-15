import os
import sys
from airflow.utils.dates import days_ago
from airflow import DAG
from airflow.operators.bash import BashOperator


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


args = {
    'owner': 'sean',
}

dag = DAG(
    dag_id='setup_parse_financial_report',
    default_args=args,
    schedule_interval='@daily',
    start_date=days_ago(1),
)

check_requirements = BashOperator(
    task_id='check_requirements',
    bash_command=f'pip install -r {EnvSetting.PROJECT_HOME}/requirements.txt',
    depends_on_past=True,
    dag=dag
)
