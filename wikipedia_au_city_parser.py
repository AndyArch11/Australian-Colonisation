from lxml import html
import requests
import csv
import re

def dms2dec(dms_str):
    dec_value = ''

    dms_str = re.sub(r'\s', '', dms_str)
    
    sign = -1 if re.search('[swSW]', dms_str) else 1
    
    numbers = [*filter(len, re.split(r'\D+', dms_str, maxsplit=4))]

    if len(numbers) > 0:
        degree = numbers[0]
        minute = numbers[1] if len(numbers) >= 2 else '0'
        second = numbers[2] if len(numbers) >= 3 else '0'
        frac_seconds = numbers[3] if len(numbers) >= 4 else '0'
        
        second += "." + frac_seconds

        dec_value = sign * (int(degree) + float(minute) / 60 + float(second) / 3600)
    
    return dec_value

base_url = 'https://en.wikipedia.org'

page = requests.get(base_url + '/wiki/List_of_towns_and_cities_in_Australia_by_year_of_settlement')
html_content = html.fromstring(page.content)
html_content = html.make_links_absolute(html_content, base_url, False)

cities = html_content.xpath('//div[@id="mw-content-text"]/div/table/tbody/tr', smart_strings=False)

city_list = []
year_column = 0
town_column = 1
state_column = 2

for row in cities:    
    #Remove trailing '\n' and 's' from year where it exists.
    city_est_dates = row[year_column].text_content().rstrip().rstrip('s')
    state = row[state_column].text_content().rstrip()

    title = ""
    href_text = ""
    href = ""
    latitude = []
    longitude = []
    established = []

    for a in row[town_column]:
        href_text = a.text_content()
        print(href_text)
        #print(state.text_content())
        attributes = a.items()
        for attr in attributes:
            if attr[0] == 'href':
                #print('href: ' + attr[1])
                href = attr[1]
                city_page = requests.get(attr[1])
                city_html_content = html.fromstring(city_page.content)
                dms_latitude = city_html_content.xpath('//span[@class="latitude"]/text()')
                #print(latitude)
                dms_longitude = city_html_content.xpath('//span[@class="longitude"]/text()')
                #print(longitude)
                established = city_html_content.xpath('//tr[th="Established"]/td/text()')
                #print(established)
                #print(city_est_dates.text_content())
            elif attr[0] == 'title':
                #print('title: ' + attr[1])
                title = attr[1]
            #else:
                #print(attr[0] + ': ' + attr[1])

    if len(href_text) > 0:
        dms_lat = ''
        dms_lon = ''
        dec_lat = 0.0
        dec_lon = 0.0
        est = ''

        #Wikipedia pages will often return multiple differing values, taking the first value where it exists
        if len(dms_latitude) > 0:
            dms_lat = dms_latitude[0]
            dec_lat = dms2dec(dms_latitude[0])
        if len(dms_longitude) > 0:
            dms_lon = dms_longitude[0]
            dec_lon = dms2dec(dms_longitude[0])
        if len(established) > 0:
            est = established[0]
        city = [title, href_text, state, href, dms_lat, dms_lon, dec_lat, dec_lon, est, city_est_dates]
        city_list.append(city)
    print('----------------------------------------------------------')

#https://en.wikipedia.org/wiki/List_of_towns_and_cities_in_Australia_by_year_of_settlement
#Title, City Name, State, wikipedia href, dms latitude, dms longitude, dec latitude, dec longitude, established date (city page), established date (parent page)
print(city_list)
with open('city_list.csv', 'w', newline='', encoding='utf-8') as csv_city_file:
    csvwriter = csv.writer(csv_city_file, dialect='excel')
    csvwriter.writerows(city_list)

#https://en.wikipedia.org/wiki/States_and_territories_of_Australia
#State, Governance, Date First Colony Established, Date of Responsible Government, wikipedia href
state_list = [['New South Wales', 'State', '1788', '1856', 'https://en.wikipedia.org/wiki/New_South_Wales'], ['Queensland', 'State', '1824', '1859', 'https://en.wikipedia.org/wiki/Queensland'], ['South Australia', 'State', '1836', '1857', 'https://en.wikipedia.org/wiki/South_Australia'], ['Tasmania', 'State', '1803', '1856', 'https://en.wikipedia.org/wiki/Tasmania'], ['Victoria', 'State', '1834', '1855', 'https://en.wikipedia.org/wiki/Victoria_(Australia)'], ['Western Australia', 'State', '1826', '1890', 'https://en.wikipedia.org/wiki/Western_Australia'], ['Australian Capital Territory', 'Internal Territory', '1823', '1988', 'https://en.wikipedia.org/wiki/Australian_Capital_Territory'], ['Jervis Bay Territory', 'Internal Territory', '1911', '1988', 'https://en.wikipedia.org/wiki/Jervis_Bay_Territory'], ['Northern Territory', 'Internal Territory', '1824', '1978', 'https://en.wikipedia.org/wiki/Northern_Territory'], ['Ashmore and Cartier Islands', 'External Territory', '', '', 'https://en.wikipedia.org/wiki/Ashmore_and_Cartier_Islands'], ['Australian Antartic Territory', 'External Territory', '1954', '1933', 'https://en.wikipedia.org/wiki/Australian_Antarctic_Territory'], ['Christmas Island', 'External Territory', '1888', '1958', 'https://en.wikipedia.org/wiki/Christmas_Island'], ['Cocos (Keeling) Islands', 'External Territory', '1825', '1955', 'https://en.wikipedia.org/wiki/Cocos_(Keeling)_Islands'], ['Coral Sea Islands', 'External Territory', '1921', '1969', 'https://en.wikipedia.org/wiki/Coral_Sea_Islands'], ['Heard Island and McDonald Islands', 'External Territory', '', '1947', 'https://en.wikipedia.org/wiki/Heard_Island_and_McDonald_Islands'], ['Norfolk Island', 'External Territory', '1788', '1914', 'https://en.wikipedia.org/wiki/Norfolk_Island']]

with open('state_list.csv', 'w', newline='', encoding='utf-8') as csv_state_file:
    csvwriter = csv.writer(csv_state_file, dialect='excel')
    csvwriter.writerows(state_list)

