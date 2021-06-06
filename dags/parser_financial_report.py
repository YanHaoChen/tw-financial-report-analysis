import os
import sys
from airflow.utils.dates import days_ago
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator
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


args = {
    'owner': 'sean',
}

dag = DAG(
    dag_id='parser_financial_report',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(2),
)

check_requirements = BashOperator(
    task_id='check_requirements',
    bash_command=f'pip install -r {EnvSetting.PROJECT_HOME}/requirements.txt',
    depends_on_past=True,
    dag=dag
)


@EnvSetting.append_project_to_path
def load_report_to_elasticsearch(**context):
    from reports.financial_report_agent import FinancialReportAgent
    from toolbox.date_tool import DateTool
    print(f'abc: {context}')
    execution_date = context['ds']
    year, month, day = map(int, execution_date.split('-'))
    season, season_year = DateTool.date_to_ex_season_and_year(year, month)
    fn_report_agent = FinancialReportAgent(2633, season_year, season, "A")

    if not fn_report_agent:
        return 'the_report_is_not_exist'

    search_balance_sheet_set = {
        'Total assets',
        'Total current assets',
        'Total non-current assets',
        'Total liabilities',
        'Total current liabilities',
        'Total non-current liabilities',
        'Total equity'
    }
    balance_sheet_res = fn_report_agent.balance_sheet.parse_items_to_dict(search_balance_sheet_set)
    print(balance_sheet_res)
    search_comprehensive_income_sheet_set = {
        'Total operating revenue',
        'Total operating costs',
        'Total basic earnings per share'
    }
    income_res = fn_report_agent.comprehensive_income_sheet.parse_items_to_dict(search_comprehensive_income_sheet_set)
    print(income_res)
    return 'done'


load_report_to_elasticsearch_task = BranchPythonOperator(
    task_id='load_report_to_elasticsearch',
    python_callable=load_report_to_elasticsearch,
    provide_context=True,
    dag=dag,
)

the_report_is_not_exist_task = DummyOperator(
    task_id='the_report_is_not_exist',
    dag=dag
)

done_task = DummyOperator(
    task_id='done',
    dag=dag
)

check_requirements >> load_report_to_elasticsearch_task >> [the_report_is_not_exist_task, done_task]
