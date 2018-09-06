import csv
import urllib.request
import html
import os
import plotly
# plotly.__version__
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.tools import FigureFactory as FF

plotly.tools.set_credentials_file(username='vickxu', api_key='23sFtKPu6WrXQVDj50gL')

from flask import redirect, render_template, request, session, url_for
from functools import wraps

# create pie graph of given values
def piechart(name, values, colours):
    """Return a pie chart for specified sentiments as HTML."""

    figure = {
        "data": [
            {
                "labels": name,
                "hoverinfo": "none",
                "marker": {
                    "colors": colours
                },
                "type": "pie",
                "values": values
            }
        ],
        "layout": {
            "showlegend": True
            }
    }
    return plotly.offline.plot(figure, output_type="div", show_link=False, link_text=False)
    
# create bar graph of monthly energy usage
def barchart(electric):
    """Return a bar chart as HTML."""

    data = [go.Bar(
            x=['September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August'],
            y=electric
    )]
    
    layout = go.Layout(
        xaxis=dict(
            title='Months',
            titlefont=dict(
                family='Arial, monospace',
                size=18,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title='Electric Energy Usage (kWh)',
            titlefont=dict(
                family='Arial, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)


    return plotly.offline.plot(fig, output_type="div", show_link=False, link_text=False)

# create bar graph of given dorm and country values
def countrychart(dorm, country, dormv, countryv):
    """Return a bar chart as HTML."""

    data = [go.Bar(
            x=[dorm, country],
            y=[dormv, countryv]
    )]
    
    layout = go.Layout(
        yaxis=dict(
            title='Electric Energy Usage (kWh)',
            titlefont=dict(
                family='Arial, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)

    return plotly.offline.plot(fig, output_type="div", show_link=False, link_text=False)
    
# create comparision bar graphs of two different entities
def comparebar(choice, values, choiceb, valuesb):
    
    trace0 = go.Bar(
        x=['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
           'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',],
        y=values,
        name= choice,
        marker=dict(
            color='rgb(49,130,189)'
        )
    )
    trace1 = go.Bar(
        x=['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
           'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',],
        y=valuesb,
        name= choiceb,
        marker=dict(
            color='rgb(204,204,204)',
        )
    )
    
    data = [trace0, trace1]
    layout = go.Layout(
        xaxis=dict(tickangle=-45),
        barmode='group',
    )
    
    fig = go.Figure(data=data, layout=layout)
    return plotly.offline.plot(fig, output_type="div", show_link=False, link_text=False)
    
# create table of energy usage values per month
def table (electric):
    """Return a table as HTML."""
    
    data_matrix = [['Dorm','Sept', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug'],
                electric
                    ]

    table = FF.create_table(data_matrix, index=True)

    # Make text size larger
    for i in range(len(table.layout.annotations)):
        table.layout.annotations[i].font.size = 20

    return plotly.offline.plot(table, output_type="div", show_link=False, link_text=False)
    
# calculate per capita energy usage per dorm
def pc(dorm, total):
    
    value = total
    if dorm == 'Apley':
        return total/28
    elif dorm == 'Hollis':
        return total/60
    elif dorm == 'Holworthy':
        return total/83
    elif dorm == 'Lionel':
        return total/34
    elif dorm == 'Mower':
        return total/34
    elif dorm == 'Greenough':
        return total/82
    elif dorm == 'Hurlbut':
        return total/56
    elif dorm == 'Pennypacker':
        return total/103
    elif dorm == 'Wigglesworth':
        return total/202
    elif dorm == 'Grays':
        return total/99
    elif dorm == 'Matthews':
        return total/150
    elif dorm == 'Weld':
        return total/154
    elif dorm == 'Canaday':
        return total/247
    elif dorm == 'Thayer':
        return total/160
    elif dorm == 'Stoughton':
        return total/57
    elif dorm == 'Straus':
        return total/95
    return value
    
def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

