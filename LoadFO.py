from sys import exc_info
from bs4 import BeautifulSoup
from shutil import copyfileobj
from os import path
from time import sleep
from urllib.request import urlopen
from json import loads
from FO import *
from SqlTlkt import *
from selenium import webdriver
import requests
import re


class LoadFO:
    def __init__(self, db_a, db, p, u, pw, k):
        self.Success = False
        self.sql = SqlTlkt(db_a, db, p, u, pw)
        self.google_api_key = k

    def get_soup(self, url):
        try:
            # driver = webdriver.Firefox()
            driver = webdriver.PhantomJS('C:/Program Files/phantomjs-2.1.1-windows/bin/phantomjs.exe')
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            driver.close()
        except:
            print("Error loading FOs file:", exc_info()[0])
            raise
        return soup

    def rip_address(self, soup):
        # Gets the third Column
        third_col_raw = soup.find('div', class_='mosaic-position-two-thirds')
        # Grabs the content
        content_raw = third_col_raw.find_all('div', {'class': 'mosaic-tile-content'})
        # Grab the address (All seem to be either in the first or second div)
        if content_raw[0].find('p'):
            addr_one = content_raw[0].find('p').find_all('br')[0].previous_sibling
            addr_two = content_raw[0].find('p').find_all('br')[0].next_sibling
            addr_three = content_raw[0].find('p').find_all('br')[1].next_sibling
        elif content_raw[1].find('p'):
            addr_one = content_raw[1].find('p').find_all('br')[0].previous_sibling
            addr_two = content_raw[1].find('p').find_all('br')[0].next_sibling
            addr_three = content_raw[1].find('p').find_all('br')[1].next_sibling

        # Check if third p tag is an address or phone number
        if addr_three:
            if self.is_phone_number(addr_three):
                ph = addr_three
                addr_three = ''
            else:
                addr_three = ', ' + addr_three
        else:
            addr_three = ''
        addr_out = '%s, %s%s' % (addr_one, addr_two, addr_three)

        # Lookup Address Lat/Long
        a_out = self.geocode_hq(addr_out)
        if a_out:
            return a_out
        else:
            return [None, None]

    def rip_fos(self, soup):
        fo_all = []
        fo_l_all = []
        try:
            lis = soup.find_all('li', {'class': 'portal-type-folder castle-grid-block-item'})
            for li in lis:
                # Lookup Name
                h3_title = li.find('h3', {'class': 'title'})
                fo_name = h3_title.find('a').get_text()

                # Lookup FOID
                fo_id = self.get_foid_by_foname(fo_name)

                # Icon
                iconurl = li.find('div', {'class': 'focuspoint'})['data-base-url']
                iconfilepath = "../images/FOImages/" + str(fo_id) + '.jpg'
                self.rip_fo_image(iconurl, iconfilepath)

                # Lookup External URL
                fo_url_external = h3_title.find('a')['href']

                # Lookup Internal URL
                fo_url_internal = None

                # Get soup from external URL (FO's Homepage)
                soup = self.get_soup(fo_url_external)

                # Lookup Address
                [fo_lat, fo_long] = self.rip_address(soup)

                fo = FieldOffice(fo_id, fo_name, iconfilepath, fo_url_external, fo_url_internal, fo_lat, fo_long)
                fo_all.append(fo)

                fo_l_all.append(self.rip_fo_leaders(fo_id, soup))
                p_added = '%s: %s, %s %s' % (fo_id, fo_name, fo_lat, fo_long)
                print(p_added)

        except:
            print("Error ripping FOs file:", exc_info()[0])
            raise

        return [fo_all, fo_l_all]

    def rip_fo_image(self, i_url, i):
        try:
            # Download the image if we don't already have it
            if not path.isfile(i):
                sleep(10)
                response = requests.get(i_url, stream=True)
                with open(i, 'wb') as out_file:
                    copyfileobj(response.raw, out_file)
                del response
                print(i_url)
        except:
            print("Error ripping FOs file:", exc_info()[0])
            raise

    def is_phone_number(self, s):
        phone_regex = re.compile(r'''(
            (\d{3}|\(\d{3}\))?            # area code
            (\s|-|\.)?                    # separator
            \d{3}                         # first 3 digits
            (\s|-|\.)                     # separator
            \d{4}                         # last 4 digits
            (\s*(ext|x|ext.)\s*\d{2,5})?  # extension
            )''', re.VERBOSE)
        match = phone_regex.search(s)
        if match:
            return True
        else:
            return False

    def geocode_hq(self, a):
        address = a.replace(" ", "+")
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (address, self.google_api_key)
        response = urlopen(url)
        jsongeocoded = loads(response.read().decode('utf-8'))
        # Return Lat & Long
        if jsongeocoded['results']:
            return [jsongeocoded['results'][0]['geometry']['location']['lat'],
                    jsongeocoded['results'][0]['geometry']['location']['lng']]
        else:
            return None

    def get_foid_by_foname(self, fn):
        strSQL = "SELECT [id] FROM [Published_FO] WHERE [FOName] = ?"
        params = []
        params = [fn]
        FOID = self.sql.get_sql_list(strSQL, params)
        if FOID[0][0]:
            return FOID[0][0]
        else:
            return None

    def get_focode_by_foid(self, id):
        strSQL = "SELECT [FOCode] FROM [Published_FO] WHERE [id] = ?"
        params = []
        params = [id]
        focode = self.sql.get_sql_list(strSQL, params)
        if focode[0][0]:
            return focode[0][0]
        else:
            return None

    def upload_fos(self, fos):
        for fo in fos:
            strSQL = "UPDATE [Published_FO] " \
                     "SET [IconFilepath] = ?, " \
                     "[FOURL] = ?, " \
                     "[FOLat] = ?, " \
                     "[FOLong] = ? " \
                     "WHERE [id] = ?;"
            params = []
            params = [fo.IconFilepath, fo.FOURL_Internal, fo.FOLat, fo.FOLong, fo.FOID]
            self.sql.run_query(strSQL, params)

    def upload_fo_leaders(self, fo_ls):
        for fo_l in fo_ls:
            strSQL = "INSERT INTO [Published_FOLeadership] " \
                     "( [FOProfileID], [FullName], [Title], [isLead] ) " \
                     "VALUES " \
                     "( ?, ?, ?, ? );"
            params = []
            params = [fo_l.foid, fo_l.FullName, fo_l.Title, fo_l.isLead]
            self.sql.RunQuery(strSQL, params)

    def rip_fo_leaders(self, foid, soup):
        # Gets the third Column
        third_col_raw = soup.find('div', class_='mosaic-position-two-thirds')
        # Grabs the content of all the data elements in the column
        content_raw = third_col_raw.find_all('div', {'class': 'mosaic-tile-content'})

        # Find the section with the H3
        for d in content_raw:
            if d.find('h3') and d.find('h3').get_text().lower() != 'contact us' \
                    and d.find('h3').get_text().lower() != 'resident agencies':
                raw_leadership = d
                break
            else:
                if d.find('h5'):
                    raw_leadership = d
                    break

        # Title is the first <h3> the name is in the first-third <p>. FIXMEWAB: Slightly brittle.
        if raw_leadership.find('h3'):
            jefe_title = raw_leadership.find('h3').get_text()
        elif raw_leadership.find('h5'):
            jefe_title = raw_leadership.find('h5').get_text()

        if raw_leadership.find('h3') or raw_leadership.find('h5'):
            if raw_leadership.find_all('p')[0]:
                jefe_name = raw_leadership.find_all('p')[0].get_text()
                jefe_name_nw = ''.join(jefe_name.split())
                if len(jefe_name_nw) > 0:
                    print(foid, jefe_name, jefe_title)
                    return [foid, jefe_name, jefe_title, 1]
            if raw_leadership.find_all('p')[1]:
                jefe_name = raw_leadership.find_all('p')[1].get_text()
                jefe_name_nw = ''.join(jefe_name.split())
                if len(jefe_name_nw) > 0:
                    print(foid, jefe_name, jefe_title)
                    return [foid, jefe_name, jefe_title, 1]
            if raw_leadership.find_all('p')[2]:
                jefe_name = raw_leadership.find_all('p')[2].get_text()
                jefe_name_nw = ''.join(jefe_name.split())
                if len(jefe_name_nw) > 0:
                    print(foid, jefe_name, jefe_title)
                    return [foid, jefe_name, jefe_title, 1]

        return None
