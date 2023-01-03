import datetime
import pandas as pd
import dash
from dash import Dash, dash_table, html, dcc, Input, Output, callback
from dash.dash_table.Format import Format, Symbol, Trim, Scheme, Group

dash.register_page(__name__,path='/jobs_breakdown',name='Jobs breakdown')

df_second_jobs_mega= pd.read_pickle('df_second_jobs_mega.pkl')
df_second_jobs_mega['Source'] = df_second_jobs_mega['Source'].apply(lambda url: f'[{url}]({url})')
filtered_data = df_second_jobs_mega.dropna(subset=['Client/Organisation'])

unique_register_dates = sorted([i for i in df_second_jobs_mega['Register date'].unique().tolist()], reverse=True)
unique_register_dates = [datetime.datetime.strftime(i,'%d %B %Y') for i in unique_register_dates]
unique_register_dates.insert(0,'All dates')

layout = html.Div([
    dcc.Markdown('''
    ### Jobs breakdown

    ...

    **Notes to reader:**
    - Each line represents an entry into the Register.
    - Empty MP entries have been removed.

    **Last updated: [12 December 2022](https://publications.parliament.uk/pa/cm/cmregmem/221212/contents.htm)**
    ''',
    style = {'fontFamily':'Arial','fontSize':14}),

    dcc.Dropdown(
        unique_register_dates,
        'All dates',
        searchable=True,
        style = {'fontFamily':'Arial','fontSize':14},
        id="jobs-breakdown-dropdown"),
    html.Br(),

    dash_table.DataTable(
        data=filtered_data.to_dict('records'),

        columns=[
            {'name':'MP Name',
            'id':'Name',
            'type':'text'},

            {'name':'Company/Client',
            'id':'Client/Organisation',
            'type':'text'},

            {'name':'Role',
            'id':'Role',
            'type':'text'},
            
            {'name':'Earnings',
            'id':'Earnings (RAW)',
            'type':'text'},
            
            {'name':'Hours worked',
            'id':'Hours worked (RAW)',
            'type':'text'},
            
            {'name':'Date',
            'id':'Date of Earnings',
            'type':'text'},
            
            {'name':'Source',
            'id':'Source',
            'presentation':'markdown',
            'type':'text'},
        ],

        style_cell_conditional = [
            {'if':{'column_id':'Name'},
            'width':'15%'},
            {'if':{'column_id':'Client/Organisation'},
            'width':'25%'},
            {'if':{'column_id':'Role'},
            'width':'25%'}
        ],

        css = [
            {'selector':'table',
            'rule':'table-layout: fixed'}
        ],

        style_table = {
            'fontFamily':'Arial',
            'fontSize':12,
            'overflowX':'auto',
            'textAlign':'left',
            'textOverflow':'ellipsis'},

        style_header = {
            'backgroundColor': '#383838',
            'fontWeight':'bold',
            'color':'white',
            'textAlign':'left'
        },

        style_data = {
            'backgroundColor':'WhiteSmoke',
            'whiteSpace':'normal',
            'height':'auto',
            'textAlign':'left'
        },

        style_filter = {
            'backgroundColor':'Snow',
        },
        filter_options = {
            'case':'insensitive'
        },

        sort_action="native",
        filter_action="native",
        id="jobs-breakdown-table"
    )
])

@callback(
    Output('jobs-breakdown-table','data'),
    Input('jobs-breakdown-dropdown','value')
)
def update_rows(selected_value):
    if selected_value == 'All dates':
        dff = filtered_data.sort_values(['Register date','Name'], ascending=[False, True])
    else:
        dff = filtered_data[filtered_data['Register date'] == datetime.datetime.strptime(selected_value,"%d %B %Y").date()].sort_values('Name',ascending=True)
    return dff.to_dict('records')