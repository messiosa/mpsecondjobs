import datetime
import pandas as pd
from dash import Dash, dash_table, html, dcc, Input, Output

df_mp_overview_mega = pd.read_pickle('df_mp_overview_mega.pkl')
df_second_jobs_mega = pd.read_pickle('df_second_jobs_mega.pkl')

app = Dash(__name__)
server = app.server

unique_register_dates = sorted([i for i in df_mp_overview_mega['Register date'].unique().tolist()], reverse=True)
unique_register_dates.append('All')

app.layout = html.Div([
    html.H2('MP Second Jobs'),

    dcc.Dropdown(
        unique_register_dates,
        'All',
        searchable=True,
        id="my-dropdown"),
    html.Br(),

    dash_table.DataTable(
        data=df_mp_overview_mega.to_dict('records'),
        columns=[
            {"name": i, "id": i} for i in df_mp_overview_mega.columns
        ],

        style_cell ={'textAlign':'left'},
        sort_action="native",
        filter_action="native",
        id="my-table"
    )
])

@app.callback(
    Output('my-table','data'),
    Input('my-dropdown','value')
)
def update_rows(selected_value):
    if selected_value == 'All':
        dff = df_mp_overview_mega
    else:
        dff = df_mp_overview_mega[df_mp_overview_mega['Register date'] == datetime.datetime.strptime(selected_value,'%Y-%m-%d').date()]
    return dff.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=False)