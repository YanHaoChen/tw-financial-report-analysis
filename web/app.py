from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px

app = Flask(__name__, template_folder='./templates')

@app.route("/")
def dashboard():
    df = pd.DataFrame({
        "field": ["roa", "roe", "roa", "roe"],
        "value": [0.0053, 0.04, 0.04, 0.0053],
        "season": ["2020-1", "2020-1", "2020-2", "2020-2"]
    })

    fig = px.bar(df, x="season", y="value", color="field", barmode="group")
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', graphJSON=graph_json)
