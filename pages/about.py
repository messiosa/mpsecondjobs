import dash
from dash import html, dcc

dash.register_page(__name__,path='/about',name='About')

layout = html.Div([
    dcc.Markdown('''
        About page will go here.
    ''',
    style={
        'fontFamily':'Arial',
        'fontSize':14})
])