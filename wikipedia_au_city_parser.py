from lxml import html
import requests
import csv
import re
import pandas as pd

base_url = 'https://en.wikipedia.org'
reg_year = re.compile(r'[1][7,8,9][0-9]{2}|[2][0][0-2][0-9]')
reg_pop = re.compile(r'\d+')
reg_dec = re.compile(r"[0-9]{1,3}[.]{1}[0-9]{1,}")

town_list = [] 
undated_town_list = []
unmapped_town_list = []

def dms2dec(dms_str):
    dec_value = 0.0

    dms_str = re.sub(r'\s', '', dms_str) #strip white space characters
    
    sign = -1 if re.search('[swSW]', dms_str) else 1 #South and West directions have a negative value

    if re.search('^[0-9]{1,3}[.]', dms_str):
        m = reg_dec.findall(dms_str)
        dec_str = m[0]
        dec_value = sign * float(dec_str)
    else:    
        numbers = [*filter(len, re.split(r'\D+', dms_str, maxsplit=4))]

        if len(numbers) > 0:
            degree = numbers[0] # A fractional degree should have already been addressed
            minute = numbers[1] if len(numbers) >= 2 else '0' # A fractional minute will be incorrectly treated as a second in this approach
            second = numbers[2] if len(numbers) >= 3 else '0'
            frac_seconds = numbers[3] if len(numbers) >= 4 else '0'
            
            second += "." + frac_seconds

            dec_value = sign * (int(degree) + float(minute) / 60 + float(second) / 3600)
    
    return dec_value

def clean_year(dirty_year):
    clean_est_year = 0

    if len(dirty_year) > 0:
        if dirty_year.isnumeric():
            clean_est_year = int(dirty_year)
        else:
            if len(dirty_year) > 4:
                try:
                    m = reg_year.search(dirty_year)
                    dirty_year = m[0]
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print("Could not process date: " + dirty_year)

            if dirty_year.isnumeric():
                clean_est_year = int(dirty_year) 

    return clean_est_year    

def clean_pop(dirty_pop):
    clean_population = 0
    dirty_concat_pop = ""

    if len(dirty_pop) > 0:
        if dirty_pop.isnumeric():
            clean_population = int(dirty_pop)
        else:            
            try:
                leading_pop = dirty_pop.split("(") # remove strings that have parenthesis in them, assumes always at end of line if they exist
                m = reg_pop.findall(leading_pop[0])
                dirty_concat_pop = ''.join(m)

            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                print("Could not process population: " + dirty_pop)

            if dirty_concat_pop.isnumeric():
                clean_population = int(dirty_concat_pop) 

    return clean_population    

def get_html_content(page_url):
    if "https://" not in page_url:
        page = requests.get(base_url + page_url)
    else:
        page = requests.get(page_url)
    html_content = html.fromstring(page.content)
    html_content = html.make_links_absolute(html_content, base_url, False)
    return html_content

def wikipedia_town_page(town_url):
    town_page = requests.get(town_url)
    town_html_content = html.fromstring(town_page.content)
    dms_latitude = town_html_content.xpath('//span[@class="latitude"]/text()')
    dms_longitude = town_html_content.xpath('//span[@class="longitude"]/text()')
    established = town_html_content.xpath('//tr[th="Established"]/td/text()')
    population = town_html_content.xpath('//tr[th="Population"]/td/text()|//tr[th="Population"]/td/ul/li/text()')

    return dms_latitude, dms_longitude, established, population

def wikipedia_town_category_page(target_state, page_url, xpath_filter, town_list, undated_town_list, unmapped_town_list):
    html_content = get_html_content(page_url)

    parse_unordered_lists(target_state, html_content, xpath_filter, town_list, undated_town_list, unmapped_town_list)

    next_page = html_content.xpath('//div[@id="mw-pages"]/a[text()="next page"][position()=1]', smart_strings=False)

    while next_page:
        html_content = get_html_content(next_page[0].attrib['href'])

        parse_unordered_lists(target_state, html_content, xpath_filter, town_list, undated_town_list, unmapped_town_list)

        next_page = html_content.xpath('//div[@id="mw-pages"]/a[text()="next page"][position()=1]', smart_strings=False)

def parse_anchor(target_state, anchor, town_list, town_est_year, undated_town_list, unmapped_town_list): 
    title = ""
    href_text = ""
    href = ""
    established = []
    follow_link = True
    state = ""
    est = 0
    pop = 0

    href_text = anchor.text_content()    
    if target_state not in (None, ""):
        state = target_state

    town_name = href_text
    if ', ' in town_name:
        split_town_name = town_name.split(', ')
        town_name = split_town_name[0]
        if target_state in (None, ""):
            state = split_town_name[1]

    #print(state.text_content())
    attributes = anchor.items()
    for attr in attributes:
        if attr[0] == 'class':
            class_attr = attr[1]
            if class_attr == 'new':
                follow_link = False
        if attr[0] == 'href':
            href = attr[1]
        elif attr[0] == 'title':
            title = attr[1]
            title_array = title.split(', ')
            if len(title_array) > 1:
                # if state is not provided as an input param, get it from either the href text or title text, with title text preferred  
                if target_state in (None, ""):                
                    state = title_array[1]

    if follow_link and len(href) > 0:
        dms_latitude, dms_longitude, established, population = wikipedia_town_page(href) 
        try:
            if established != None and len(established) > 0:
                est = clean_year(established[0])
        except Exception as err:
            print("Failed parsing date: " + established[0])
            print(f"While parsing date encountered unexpected {err=}, {type(err)=}")
        
        if (est in (None, "") or est == 0) and town_est_year != None:
            est = town_est_year

        try:
            if population != None and len(population) > 0:
                pop = clean_pop(population[0])
        except Exception as err:
                pop = 0

        print("State: " + state + ", Town Name: " + town_name + ", est date " + str(est))
        if len(dms_latitude) > 0 and len(dms_longitude):
            print("lat: " + dms_latitude[0] + ", lon: " + dms_longitude[0])      

        if len(town_name) > 0:
            dms_lat = ''
            dms_lon = ''
            dec_lat = 0.0
            dec_lon = 0.0

            #Wikipedia pages will often return multiple differing values, taking the first value where it exists
            if len(dms_latitude) > 0:
                dms_lat = dms_latitude[0]
                dec_lat = dms2dec(dms_latitude[0])
            if len(dms_longitude) > 0:
                dms_lon = dms_longitude[0]
                dec_lon = dms2dec(dms_longitude[0])
            if not state:
                state = target_state
            
            # only record town if we can map it            
            town = [town_name, title, href_text, state, href, dms_lat, dms_lon, dec_lat, dec_lon, est, town_est_year, pop]
            if est > 0 and dec_lat < 0 and dec_lon > 0:
                town_list.append(town)
                print("Title: " + title + ", Est. Date: " + str(est) + ", dec Lat: " + str(dec_lat) + ", dec Lon: " + str(dec_lon))
            elif dec_lat < 0 and dec_lon > 0:
                undated_town_list.append(town)
            else:
                print(title + " not mapped")
                unmapped_town_list.append(town)
    else:
        town = [town_name, title, href_text, state, href, None, None, 0, 0, None, None, None]
        unmapped_town_list.append(town)
    print('----------------------------------------------------------')

def parse_unordered_lists(target_state, html_content, xpath_filter, town_list, undated_town_list, unmapped_town_list):

    towns = html_content.xpath(xpath_filter, smart_strings=False)

    for row in towns:   
        parse_anchor(target_state, row, town_list, None, undated_town_list, unmapped_town_list)

def towns_and_cities_by_settlement_date(town_list, undated_town_list, unmapped_town_list):

    html_content = get_html_content('/wiki/List_of_towns_and_cities_in_Australia_by_year_of_settlement')

    towns = html_content.xpath('//div[@id="mw-content-text"]/div/table/tbody/tr[position()>1]', smart_strings=False)

    year_column = 0
    town_column = 1
    state_column = 2

    for row in towns:    
        #Remove trailing '\n' and 's' from year where it exists.
        #town_est_dates = row[year_column].text_content().rstrip().rstrip('s')
        town_est_dates = clean_year(row[year_column].text)
        state = row[state_column].text_content().rstrip()

        #parse HTML table
        for a in row[town_column]:
            parse_anchor(state, a, town_list, town_est_dates, undated_town_list, unmapped_town_list)                 

def towns_in_australia(town_list, undated_town_list, unmapped_town_list):

    html_content = get_html_content('/wiki/List_of_towns_in_Australia')

    #Town mappings for Canberra, New South Wales, Northern Territory, and Queensland
    parse_unordered_lists("", html_content, '//div[@class="div-col"]/ul/li/* | //div[@class="hatnote navigation-not-searchable"]/following::ul[position()=1]/li/*', town_list, undated_town_list, unmapped_town_list)

def towns_in_act(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('Australian Capital Territory', '/wiki/Category:Towns_in_the_Australian_Capital_Territory', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def towns_in_nsw(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('New South Wales', '/wiki/Category:Towns_in_New_South_Wales', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def towns_in_nt(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('Northern Territory', '/wiki/Category:Towns_in_the_Northern_Territory', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def towns_in_qld(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('Queensland', '/wiki/Category:Towns_in_Queensland', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def towns_in_sa(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('South Australia', '/wiki/Category:Towns_in_South_Australia', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def towns_in_tas(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('Tasmania', '/wiki/Category:Towns_in_Tasmania', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def towns_in_vic(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('Victoria', '/wiki/Category:Towns_in_Victoria_(state)', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def towns_in_wa(town_list, undated_town_list, unmapped_town_list):
    wikipedia_town_category_page('Western Australia', '/wiki/Category:Towns_in_Western_Australia', '//div[@class="mw-category-group"]/ul/li/*[not(self::div[@class="CategoryTreeSection"])]', town_list, undated_town_list, unmapped_town_list)

def sanitise_town_list(place_list):
    #TODO remove state from town name
    print("Town List size before clean: " + str(len(place_list)))

    df = pd.DataFrame(place_list)

    place_list = list((df.drop_duplicates(subset=[4], keep='first')).values)

    print("Town List size after clean: " + str(len(place_list)))

    return place_list


def states():
    #https://en.wikipedia.org/wiki/States_and_territories_of_Australia
    #State, Governance, Date First Colony Established, Date of Responsible Government, wikipedia href
    state_list = [['New South Wales', 'State', '1788', '1856', 'https://en.wikipedia.org/wiki/New_South_Wales'], ['Queensland', 'State', '1824', '1859', 'https://en.wikipedia.org/wiki/Queensland'], ['South Australia', 'State', '1836', '1857', 'https://en.wikipedia.org/wiki/South_Australia'], ['Tasmania', 'State', '1803', '1856', 'https://en.wikipedia.org/wiki/Tasmania'], ['Victoria', 'State', '1834', '1855', 'https://en.wikipedia.org/wiki/Victoria_(Australia)'], ['Western Australia', 'State', '1826', '1890', 'https://en.wikipedia.org/wiki/Western_Australia'], ['Australian Capital Territory', 'Internal Territory', '1823', '1988', 'https://en.wikipedia.org/wiki/Australian_Capital_Territory'], ['Jervis Bay Territory', 'Internal Territory', '1911', '1988', 'https://en.wikipedia.org/wiki/Jervis_Bay_Territory'], ['Northern Territory', 'Internal Territory', '1824', '1978', 'https://en.wikipedia.org/wiki/Northern_Territory'], ['Ashmore and Cartier Islands', 'External Territory', '', '', 'https://en.wikipedia.org/wiki/Ashmore_and_Cartier_Islands'], ['Australian Antartic Territory', 'External Territory', '1954', '1933', 'https://en.wikipedia.org/wiki/Australian_Antarctic_Territory'], ['Christmas Island', 'External Territory', '1888', '1958', 'https://en.wikipedia.org/wiki/Christmas_Island'], ['Cocos (Keeling) Islands', 'External Territory', '1825', '1955', 'https://en.wikipedia.org/wiki/Cocos_(Keeling)_Islands'], ['Coral Sea Islands', 'External Territory', '1921', '1969', 'https://en.wikipedia.org/wiki/Coral_Sea_Islands'], ['Heard Island and McDonald Islands', 'External Territory', '', '1947', 'https://en.wikipedia.org/wiki/Heard_Island_and_McDonald_Islands'], ['Norfolk Island', 'External Territory', '1788', '1914', 'https://en.wikipedia.org/wiki/Norfolk_Island']]

    with open('./data/state_list.csv', 'w', newline='', encoding='utf-8') as csv_state_file:
        csvwriter = csv.writer(csv_state_file, dialect='excel')
        csvwriter.writerows(state_list)

#city mappings   
towns_and_cities_by_settlement_date(town_list, undated_town_list, unmapped_town_list)

#Town mappings for Canberra, New South Wales, Northern Territory, and Queensland
towns_in_australia(town_list, undated_town_list, unmapped_town_list)

#Town mappings of ACT
towns_in_act(town_list, undated_town_list, unmapped_town_list)

#Town mappings of New South Wales
towns_in_nsw(town_list, undated_town_list, unmapped_town_list)

#Town mappings of Northern Territory
towns_in_nt(town_list, undated_town_list, unmapped_town_list)

#Town mappings in Queensland
towns_in_qld(town_list, undated_town_list, unmapped_town_list)

#Town mappings of South Australia
towns_in_sa(town_list, undated_town_list, unmapped_town_list)

#Town mappings of Tasmania
towns_in_tas(town_list, undated_town_list, unmapped_town_list)

#Town mappings of Victoria
towns_in_vic(town_list, undated_town_list, unmapped_town_list)

#Town mappings of Western Australia
towns_in_wa(town_list, undated_town_list, unmapped_town_list)


print("Deduping Town List")
town_list = sanitise_town_list(town_list)

print("Deduping Undated Town List")
undated_town_list = sanitise_town_list(undated_town_list)

print("Deduping Unmapped Town List")
unmapped_town_list = sanitise_town_list(unmapped_town_list)

#Town Name, Title, href text, State, wikipedia href, dms latitude, dms longitude, dec latitude, dec longitude, established date (city page), established date (parent page), population
#print(town_list)
with open('./data/city_list.csv', 'w', newline='', encoding='utf-8') as csv_city_file:
    csvwriter = csv.writer(csv_city_file, dialect='excel')
    csvwriter.writerows(town_list)

with open('./data/undated_city_list.csv', 'w', newline='', encoding='utf-8') as csv_city_file:
    csvwriter = csv.writer(csv_city_file, dialect='excel')
    csvwriter.writerows(undated_town_list)

with open('./data/unmapped_city_list.csv', 'w', newline='', encoding='utf-8') as csv_city_file:
    csvwriter = csv.writer(csv_city_file, dialect='excel')
    csvwriter.writerows(unmapped_town_list)

#states()



