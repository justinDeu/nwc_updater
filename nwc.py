import requests
import gspread
import logging
import time
import numpy as np
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

eastern = timezone('US/Eastern')

logging.basicConfig(
    filename='app.log',
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class School():
    def __init__(self, name, loc, link, starting):
        self.name = name
        self.loc = loc
        self.link = link
        self.sess = requests.Session()
        self.starting = starting
        self.curr_amount = self.get_current_total()
        self.diffs = []

    def get_current_total(self):
        page = self.sess.get(self.link)
        soup = BeautifulSoup(page.text, 'html.parser')
        dollars = soup.find('span', class_='dollars')
        return float(dollars.contents[1].replace(',', ''))

    def update_total(self):
        t = self.get_current_total()

        self.diffs.append(t - self.curr_amount)

        if len(self.diffs) > 60:
            self.diffs.pop(0)

        self.curr_amount = t
        return self.curr_amount

    def nwc_amount(self):
        return self.curr_amount - self.starting

    def past_hour(self):
        return sum(self.diffs)

def auth_sheet():
    global eastern
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials_sheets.json', scope)

    client = gspread.authorize(creds)

    sheet = client.open('NWC Updater').sheet1
    logging.info('Google Sheet Authorized')
    sheet.update_acell('B12', str(datetime.now(eastern)))
    return sheet


schools = {
    'VT': School('VT', 2, 'https://secure.acsevents.org/site/TR/RelayForLife/RFLCY20SER?pg=entry&fr_id=95544', 200746),
    'USC': School('USC', 3, 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95442', 53928),
    'JMU': School('JMU', 4, 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95081', 103492),
    'UCLA': School('UCLA', 5, 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95209',36808),
    'UGA': School('UGA', 6, 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=94930', 121353),
    'FSU': School('FSU', 7, 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95126', 80465),
    'UMI':School('UMI', 8, 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95091', 122442),
}

logging.info('Initialzing connections to Google Sheet...')
sheet = auth_sheet()
logging.info('Connection to Google Sheet Initialized!')

# updating running since cell
sheet.update_acell('B10', str(datetime.now(eastern)))


# Loop to update sheet
while True:

    logging.info('Beginning Update...')

    try:
        school_data = sheet.range('A2:D8')
        school_data = np.reshape(school_data, (len(schools), -1))

        for row in school_data:
            school = schools[row[0].value]
            school.update_total()

            row[1].value = f'{school.nwc_amount():.2f}'
            row[2].value = f'{school.curr_amount:.2f}'
            row[3].value = f'{school.past_hour():.2f}'


        sheet.update_cells(list(np.ravel(school_data)))
        sheet.update_acell('B11', str(datetime.now(eastern)))

        logging.info('Update Completed!')
        time.sleep(60)
    except gspread.exceptions.APIError:
        logging.error('GSpread APIError occurred, reauthorizing and trying again')
        sheet = auth_sheet()
        continue
