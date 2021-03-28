from airflow.utils.dates import days_ago

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator


args = {
    'owner': 'sean',
}

dag = DAG(
    dag_id='parser_financial_report',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(2),
)


def start_parsing(**op_kwargs):

    from reports.financial_report_agent import FinancialReportAgent
    ti = op_kwargs['ti']
    print(ti)
    fn_report_agent = FinancialReportAgent(2605, 2020, 3, "C")
    print((fn_report_agent))
    if not fn_report_agent:
        print('can\'t find')
        return

    """
    1XXX:資產總計, Total assets
    2XXX:負債總計
    3XXX:權益總額
    """
    search_set = {'資產總計', '負債總計', 'Total assets'}
    result = fn_report_agent.parser_balance_sheet(search_set)
    print(result)
    return 'Whatever you return gets printed in the logs'


run_this = PythonVirtualenvOperator(
    task_id='start_parsing',
    python_callable=start_parsing,
    requirements=["beautifulsoup4", "requests"],
    system_site_packages=False,
    op_kwargs={'ti': '{{ ti }}'},
    dag=dag,
)
