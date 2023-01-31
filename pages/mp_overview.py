import datetime, os
import pandas as pd
import dash
from dash import dash_table, html, dcc, Input, Output, callback
from dash.dash_table.Format import Format, Symbol, Trim, Scheme, Group

dash.register_page(__name__, path='/', name='Summary', title="MP Second Jobs")

df_mp_overview = pd.read_pickle('df_mp_overview.pkl')
df_mp_overview_mega = pd.read_pickle('df_mp_overview_mega.pkl')

# Get date and date_words
with open('latest_scrape_date.txt','r') as f:
    date = f.read()
date_words = datetime.datetime.strftime(datetime.datetime.strptime(date,'%y%m%d'),'%d %B %Y')

layout = html.Div([
    dcc.Markdown('''
    ### Welcome to MP Second Jobs! 
    
    **Do you want to know about the extra income earned by UK MPs and the hours they spend working outside of Parliament?**

    While this information (and more) is publicly available in the [Register of Members' Financial Interests](https://www.parliament.uk/mps-lords-and-offices/standards-and-financial-interests/parliamentary-commissioner-for-standards/registers-of-interests/register-of-members-financial-interests/), it can be difficult to find and understand. That's why MP Second Jobs was created - to make this important democratic resource more accessible and insightful to members of the public, journalists, and researchers.

    ---

    **Navigating the site**
    
    - On this page, you'll find a summary of **total earnings** and **total hours worked** year-to-date (YTD) for each current MP. 
    
    - You can **filter** columns to narrow down the data (e.g., to a particular region or political party) and **order** the data using the column header arrows.
    
    - On the [Jobs](/jobs) page, you'll find a more detailed breakdown of the earnings summarised here - including who MPs are working for and what they're doing.

    - A new version of the Register is generally released every two weeks. The data below is for the most recent update to the Register - but you can download **historical data** using the **Download** button below (file size: ~4.5MB).

    - For more information about the codebase and methodology, see the [About](/about) page.

    ---

    **Last updated: ['''+date_words+'''](https://publications.parliament.uk/pa/cm/cmregmem/'''+date+'''/contents.htm)**

    ''',
    style = {'fontFamily':'Arial','fontSize':14}),

    html.Div([
        html.Button("Download historical data (.csv)", id="btn_csv1"),
        dcc.Download(id="download-dataframe-csv1")
    ]),
    html.Br(),

    dash_table.DataTable(
        data=df_mp_overview.to_dict('records'),

        columns = [
            {'name':'MP Name',
            'id':'Name',
            'type':'text'},

            {'name':'Political Party',
            'id':'Political Party',
            'type':'text'},

            {'name':'Constituency',
            'id':'Constituency',
            'type':'text'},

            {'name':'Earnings YTD',
            'id':'Secondary Earnings YTD (£)',
            'type':'numeric',
            'format':Format().scheme(Scheme.fixed).precision(2).trim(Trim.yes).group(Group.yes).symbol(Symbol.yes).symbol_prefix('£')},

            {'name':'Hours worked YTD',
            'id':'Secondary Hours Worked YTD',
            'type':'numeric',
            'format':Format().scheme(Scheme.fixed).precision(2).trim(Trim.yes).group(Group.yes).symbol(Symbol.yes).symbol_suffix(' hrs')},

            {'name':'Region',
            'id':'Region',
            'type':'text'},

            {'name':'Country',
            'id':'Country',
            'type':'text'},
        ],

        css = [
            {'selector':'table',
            'rule':'table-layout: fixed'}
        ],

        style_cell = {
            'textAlign':'left',
            'textOverflow':'ellipsis'},
        style_cell_conditional = [
            {'if':{'column_id':'Name'},
                'width':'100px',
                },
            {'if':{'column_id':'Political Party'},
                'width':'100px',
                },
            {'if':{'column_id':'Constituency'},
                'width':'100px',
                },
            {'if':{'column_id':'Secondary Earnings YTD (£)'},
                'width':'100px',
                },
            {'if':{'column_id':'Secondary Hours Worked YTD'},
                'width':'100px',
                },
            {'if':{'column_id':'Region'},
                'width':'100px',
                },
            {'if':{'column_id':'Country'},
                'width':'100px',
                }, 
        ],

        style_header = {
            'backgroundColor': '#383838',
            'fontWeight':'bold',
            'color':'white'
        },

        style_data = {
            'backgroundColor':'WhiteSmoke'
        },

        style_filter = {
            'backgroundColor':'Snow',
        },
        filter_options = {
            'case':'insensitive'
        },

        sort_action="native",
        filter_action="native",
        id="mp-overview-table"
    )
])

@callback(
    Output("download-dataframe-csv1", "data"),
    Input("btn_csv1", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df_mp_overview_mega.to_csv, "mp_summary_data_allyears.csv")