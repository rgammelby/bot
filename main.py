import requests
import time
import datetime
import os
from bs4 import BeautifulSoup
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

# <editor-fold desc="E-mail Mechanics">

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('ENV_MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('ENV_MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# </editor-fold>

# <editor-fold desc="Connections and Declarations">

# sets url for crawler
dba_url = 'https://www.dba.dk/soeg/?soeg=star+trek+voyager&sort=listingdate-desc'
response = requests.get(dba_url)  # checks response

# reports response and connection if successful
print(response)
if '200' in str(response):
    print("Connection successful. \n")
else:
    print("Connection failed. \n")

# parses information from the chosen url
soup = BeautifulSoup(response.text, "html.parser")

# finder alle elementer med tagget <a class="listingLink"></a>; alle titler m. links
tags = soup.findAll('a', class_='listingLink')

# initial declaration of sample/comparison lists (on start)
stv_listings = []
stv_links = []
stv_images = []

# runtime declaration
runtime = 0

# action list declaration
act_listings = []
act_links = []
act_images = []

# </editor-fold>

# <editor-fold desc="Main loop">

# program main loop
while (True):
    # current time
    ct = datetime.datetime.now()

    # extracts all titles
    for n in range(0, len(tags)):
        act_listings.append(tags[n].text)
        act_listings.append('*')

    # extracts listing links
    for i in soup.findAll('a', class_="listingLink", href=True):
        act_links.append(i.get('href'))

    # extracts image links
    for img in soup.findAll('img'):
        act_images.append(img.get('src'))

    # imports data if stv_listings is empty
    if not stv_listings:
        stv_listings = act_listings
        stv_images = act_images
        stv_links = act_links

    # comparison list declaration
    comp = list(set(act_listings) - set(stv_listings))

    if comp:
        print(f'Difference between sample and action lists: {comp}')
        # e-mail me the contents of 'comp'

        @app.route("/")
        def index():
            msg = Message('Hej!',
                          sender=('Spiderbot', 'srb.gammelby@gmail.com'),
                          recipients=['rab.gammelby@gmail.com'])
            msg.html = f'En <a href=\'{act_links[0]}\'>ny artikel</a> for Star Trek: Voyager ' \
                       f'er blevet slået op på dette tidspunkt: <br>{ct} <br>' \
                       f'<a href=\'{act_links[0]}\'>Link</a><br>' \
                       f'<img src=\'{act_images[0]}\' alt=\'{act_listings[0]}\'>'
            mail.send(msg)
            return "E-mail has been sent. "

        # if __name__ == '__main__':
        #     app.run(debug=True)

        stv_listings = act_listings
        images = act_images
        links = act_links
    else:
        print("No news. ")

    if runtime < 60:
        print(f'Runtime: {runtime} seconds. {ct}')
    elif 60 < runtime < 3600:
        print(f'Runtime: {runtime // 60} minutes and {runtime % 60} seconds. {ct} ')
    elif 3600 < runtime < 7200:
        print(f'Runtime: {runtime // 3600} hour, {(runtime // 60) - ((runtime // 3600) * 60)} minutes and {runtime % 60} seconds.  {ct}')
    elif 86400 > runtime > 7200:
        print(f'Runtime: {runtime // 3600} hours, {(runtime // 60) - ((runtime // 3600) * 60)} minutes and {runtime % 60} seconds.  {ct}')
    elif runtime > 86400:
        print(f'Runtime: {runtime // 86400} days, {(runtime // 3600) % 24} hours, {(runtime // 60) - ((runtime // 3600) * 60)} minutes and {runtime % 60} seconds.  {ct}')

    time.sleep(10)
    runtime += 10

# </editor-fold>