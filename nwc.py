import requests
from bs4 import BeautifulSoup

links = {
    'VT': 'https://secure.acsevents.org/site/TR/RelayForLife/RFLCY20SER?pg=entry&fr_id=95544',
    'USC': 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95442',
    'JMU': 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95081',
    'UCLA': 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95209',
    'UGA': 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=94930',
    'FSU': 'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95126',
    'UMI':'https://secure.acsevents.org/site/STR?pg=entry&fr_id=95091'
}

starting_amounts = {
    'VT': 200746,
    'USC': 53927.97,
    'JMU': 103492,
    'UCLA': 36808,
    'UGA': 121353,
    'FSU': 80465,
    'UMI':122442
}

def get_current_total(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    dollars = soup.find('span', class_='dollars')
    return float(dollars.contents[1].replace(',', ''))

print(' School |   Total   |  So Far')

for school, link in links.items():
    curr_total = get_current_total(link)
    diff = curr_total - starting_amounts[school]
    print(f'{school:^8}|{curr_total:^11.2f}|{diff:^10.2f}')