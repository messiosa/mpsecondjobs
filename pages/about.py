import dash
from dash import html, dcc

dash.register_page(__name__,path='/about',name='About',title="MP Second Jobs / About")

layout = html.Div([
    dcc.Markdown('''
        MP Second Jobs was built and is maintained by **Andrew Kyriacos-Messios**. It uses python and machine-learning to parse and structure the data contained in the [Register of Members' Financial Interests](https://www.parliament.uk/mps-lords-and-offices/standards-and-financial-interests/parliamentary-commissioner-for-standards/registers-of-interests/register-of-members-financial-interests/).

        - For the full codebase, training data, and methodology, please visit the [GitHub](https://github.com/messiosa/mpsecondjobs).

        - To learn more about the Register, go to [this](https://publications.parliament.uk/pa/cm201719/cmcode/1882/188204.htm#_idTextAnchor017) page.

        - To get in touch, contact me using [Linktree](https://linktr.ee/andrewkm) or at [andrew.messios@gmail.com](mailto:andrew.messios@gmail.com).
    ''',
    style={
        'fontFamily':'Arial',
        'fontSize':14}),
    
    html.Br(),
    html.Img(
        src='assets/bmc_qr.png',
        style={
            'height':'200px',
            'width':'200px',
            'margin':'0 auto',
            'display':'block'
        })
])