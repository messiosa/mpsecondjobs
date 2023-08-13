import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)
server = app.server

navbar = html.Div([
        html.Span('MP Second Jobs', className='navbar-title', style={'margin':'0 30px 0 0','color':'white','fontSize':20}),
        dcc.Link('Summary', href='/', className='navbar-link', style={'margin':'0 15px 0 0','color':'white','fontSize':16}),
        html.Span('/', className='navbar-title', style={'margin':'0 15px 0 0','color':'white','fontSize':20}),
        dcc.Link('Jobs', href='/jobs', className='navbar-link', style={'margin':'0 15px 0 0','color':'white','fontSize':16}),
        html.Span('/', className='navbar-title', style={'margin':'0 15px 0 0','color':'white','fontSize':20}),
        dcc.Link('About', href='/about', className='navbar-link', style={'margin':'0 15px 0 0','color':'white','fontSize':16}),
        ],

    style = {
        'fontFamily':'Arial',
        'fontWeight':'bold',
        'display':'flex',
        'justifyContent':'flex-start',
        'alignItems':'center',
        'backgroundColor': '#383838',
        'padding':'10px'},
    className='navbar')

app.layout = html.Div([
    navbar,
	dash.page_container
])

if __name__ == "__main__":
    app.run_server(debug=True)