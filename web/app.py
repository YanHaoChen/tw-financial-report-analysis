import json
import logging
import plotly
import plotly.express as px
from flask import Flask, render_template
import pandas as pd
from pymongo import MongoClient
from urllib.parse import quote_plus

uri = "mongodb://%s:%s@%s:%s/%s" % (
    quote_plus('airflower'),
    quote_plus('money'),
    '127.0.0.1',
    '27017',
    'stock'
)
stock_db = MongoClient(uri).stock

app = Flask(__name__, template_folder='./templates')

@app.route("/")
def dashboard():
    financial_report_data = pd.DataFrame(stock_db.financialReports.find({}))
    financial_report_data['stockCode'] = financial_report_data['stockCode'].astype(str)
    roa_fig = px.bar(financial_report_data, x="yearAndSeason", y="roa", color="stockCode", barmode="group")
    roa_fig.update_layout(xaxis_type='category')
    roa_fig.update_xaxes(categoryorder='category ascending')
    roa_json = json.dumps(roa_fig, cls=plotly.utils.PlotlyJSONEncoder)

    roe_fig = px.bar(financial_report_data, x="yearAndSeason", y="roe", color="stockCode", barmode="group")
    roe_fig.update_layout(xaxis_type='category')
    roe_fig.update_xaxes(categoryorder='category ascending')
    roe_json = json.dumps(roe_fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', roaJson=roa_json, roeJson=roe_json)

if __name__ == '__main__':
    app.run()