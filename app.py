import dash
from dash import Dash, html, dcc
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.message import EmailMessage

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

### EMAIL SCHEDULER ###

WEBSITE_URL = "https://publications.parliament.uk/pa/cm/cmregmem/contents2223.htm"
prev_content = ""

def check_website_updates():
    global prev_content
    response = requests.get(WEBSITE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    new_content = str(soup)

    if prev_content and prev_content != new_content:
        send_email()
    prev_content = new_content

def send_email():
    msg = EmailMessage()
    msg.set_content('The website has been updated!')
    msg['Subject'] = 'Website Update Notification'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = 'your_email@gmail.com'
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login('your_email@gmail.com', 'your_password')
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_website_updates, trigger="interval", seconds=3600)
scheduler.start()

if __name__ == "__main__":
    app.run_server(debug=True)