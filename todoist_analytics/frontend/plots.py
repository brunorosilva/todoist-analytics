import datetime
from pandas import DataFrame

import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from plotly.missing_ipywidgets import FigureWidget
from plotly.subplots import make_subplots

def completed_tasks_per_day(completed_tasks:DataFrame) -> FigureWidget:
    daily_completed_tasks = completed_tasks[['completed_date', 'project_id', 'id', 'content']].groupby(
        ['completed_date'], as_index=False).nunique()
    daily_completed_tasks['completed_date'] = daily_completed_tasks['completed_date'].astype(str)
    fig = px.bar(daily_completed_tasks, x="completed_date", y="id",
                 title='Daily completed tasks', hover_name='project_id')
    
    return fig


def display_year(z,
                 year: int = None,
                 month_lines: bool = True,
                 fig=None,
                 row: int = None):

    if year is None:
        year = datetime.datetime.now().year

    data = np.ones(365) * np.nan
    data[:len(z)] = z

    d1 = datetime.date(year, 1, 1)
    d2 = datetime.date(year, 12, 31)

    delta = d2 - d1

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                   'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_days = [31,    28,    31,     30,    31,
                  30,    31,    31,    30,    31,    30,    31]
    month_positions = (np.cumsum(month_days) - 15)/7

    # gives me a list with datetimes for each day a year
    dates_in_year = [d1 + datetime.timedelta(i) for i in range(delta.days+1)]
    # gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays
    weekdays_in_year = [i.weekday() for i in dates_in_year]

    weeknumber_of_dates = [int(i.strftime("%V")) if not (int(i.strftime("%V")) == 1 and i.month == 12) else 53
                           for i in dates_in_year]  # gives [1,1,1,1,1,1,1,2,2,2,2,2,2,2,…] name is self-explanatory
    # gives something like list of strings like ‘2018-01-25’ for each date. Used in data trace to make good hovertext.
    text = [str(i) for i in dates_in_year]
    # 4cc417 green #347c17 dark green
    colorscale = [[False, '#eeeeee'], [True, '#76cf63']]

    # handle end of year

    data = [
        go.Heatmap(
            x=weeknumber_of_dates,
            y=weekdays_in_year,
            z=data,
            text=text,
            hoverinfo='text',
            xgap=3,  # this
            ygap=3,  # and this is used to make the grid-like apperance
            showscale=False,
            colorscale=colorscale
        )
    ]

    if month_lines:
        kwargs = dict(
            mode='lines',
            line=dict(
                color='#9e9e9e',
                width=1
            ),
            hoverinfo='skip'

        )
        for date, dow, wkn in zip(dates_in_year,
                                  weekdays_in_year,
                                  weeknumber_of_dates):
            if date.day == 1:
                data += [
                    go.Scatter(
                        x=[wkn-.5, wkn-.5],
                        y=[dow-.5, 6.5],
                        **kwargs
                    )
                ]
                if dow:
                    data += [
                        go.Scatter(
                            x=[wkn-.5, wkn+.5],
                            y=[dow-.5, dow - .5],
                            **kwargs
                        ),
                        go.Scatter(
                            x=[wkn+.5, wkn+.5],
                            y=[dow-.5, -.5],
                            **kwargs
                        )
                    ]

    layout = go.Layout(
        title='activity chart',
        height=250,
        yaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            autorange="reversed"
        ),
        xaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=month_names,
            tickvals=month_positions
        ),
        font={'size': 10, 'color': '#9e9e9e'},
        plot_bgcolor=('#fff'),
        margin=dict(t=40),
        showlegend=False
    )

    if fig is None:
        fig = go.Figure(data=data, layout=layout)
    else:
        fig.add_traces(data, rows=[(row+1)]*len(data), cols=[1]*len(data))
        fig.update_layout(layout)
        fig.update_xaxes(layout['xaxis'])
        fig.update_yaxes(layout['yaxis'])

    return fig


def calendar_plot(z, years) -> FigureWidget:
    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years)
    for i, year in enumerate(years):
        data = z[i*365: (i+1)*365]
        display_year(data, year=year, fig=fig, row=i)
        fig.update_layout(height=250*len(years))

    return fig
