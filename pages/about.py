import dash
from dash import html, dcc

dash.register_page(__name__,path='/about',name='About')

layout = html.Div([
    dcc.Markdown('''
        MP Second Jobs was built by **Andrew Kyriacos-Messios**. It uses python and machine-learning to parse and structure the data contained in the Register.

        For the full codebase and methodology, please visit the [GitHub](https://github.com/messiosa/mpsecondjobs).

        To get in touch, contact me using [Linktree](https://linktr.ee/andrewkm) or at [andrew.messios@gmail.com](mailto:andrew.messios@gmail.com).
    ''',
    style={
        'fontFamily':'Arial',
        'fontSize':14})
])