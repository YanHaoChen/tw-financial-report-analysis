import os

from airflow.utils.dates import days_ago

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
PROJECT_HOME = f'{AIRFLOW_HOME}/dags/tw-financial-report-analysis'

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
    bash_command=f'pip install -r {PROJECT_HOME}/requirements.txt',
    depends_on_past=True,
    dag=dag
)


def start_parsing(*args, **op_kwargs):
    import sys
    sys.path.append(PROJECT_HOME)
    from reports.financial_report_agent import FinancialReportAgent
    fn_report_agent = FinancialReportAgent(2605, 2020, 3, "C")
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
    return


start_parsing = PythonOperator(
    task_id='start_parsing',
    python_callable=start_parsing,
    dag=dag,
)

check_requirements >> start_parsing

