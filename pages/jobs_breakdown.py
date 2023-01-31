import datetime, os
import pandas as pd
import dash
from dash import dash_table, html, dcc, Input, Output, callback

dash.register_page(__name__,path='/jobs',name='Jobs', title="MP Second Jobs / Jobs")

df_second_jobs_mega= pd.read_pickle('df_second_jobs_mega.pkl')
df_second_jobs_mega['Source'] = df_second_jobs_mega['Source'].apply(lambda url: f'[{url}]({url})')
filtered_data_mega = df_second_jobs_mega.dropna(subset=['Client/Organisation'])

df_second_jobs = pd.read_pickle('df_second_jobs.pkl')
df_second_jobs['Source'] = df_second_jobs['Source'].apply(lambda url: f'[{url}]({url})')
filtered_data = df_second_jobs.dropna(subset=['Client/Organisation'])

# Get date and date_words
with open('latest_scrape_date.txt','r') as f:
    date = f.read()
date_words = datetime.datetime.strftime(datetime.datetime.strptime(date,'%y%m%d'),'%d %B %Y')

layout = html.Div([
    dcc.Markdown('''
    ### Jobs breakdown

    - You can **filter** columns to narrow down the data (e.g., for a particular role or employer) and **order** the data using the column header arrows. 
    
    - Follow the **Source** link to read the original Register entry on [parliament.uk](https://www.parliament.uk/).

    - Each line in the table represents an entry into the Register.

    - Empty MP entries have been removed.

    - A new version of the Register is generally released every two weeks. The data below is for the most recent update to the Register - but you can download **historical data** using the **Download** button below (file size: ~40MB).
    
    ---

    **Last updated: ['''+date_words+'''](https://publications.parliament.uk/pa/cm/cmregmem/'''+date+'''/contents.htm)**
    ''',
    style = {'fontFamily':'Arial','fontSize':14}),

    html.Div([
        html.Button("Download historical data (.csv)", id="btn_csv2"),
        dcc.Download(id="download-dataframe-csv2")
    ]),
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
    Output("download-dataframe-csv2", "data"),
    Input("btn_csv2", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(filtered_data_mega.to_csv, "mp_jobs_data_allyears.csv")