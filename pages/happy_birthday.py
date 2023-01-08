import dash
from dash import html, dcc

dash.register_page(__name__,path='/happy_birthday',name='Happy Birthday',title="Happy Birthday!")

layout = html.Div([
    dcc.Markdown('''
    ### Happy happy happy Birthday!

    My gift to you: IOU one of these.

    Love,
    Andrew xxx
    ''',
    style={'fontFamily':'Arial','fontSize':14}),

    html.Img(src='assets/dalle_boat.png',style={'height':'400px','width':'400px'}),


])