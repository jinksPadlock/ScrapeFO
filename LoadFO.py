from sys import exc_info
from bs4 import BeautifulSoup
from shutil import copyfileobj
from os import path
from time import sleep
import requests
# from FO import *
from SqlTlkt import *

from selenium import webdriver

# import os.path
# import shutil


class LoadFO:
    def __init__(self, db, u, p):
        self.Success = False
        self.sql = SqlTlkt(db, u, p)

    def download_fos(self, url):
        try:
            # driver = webdriver.Firefox()
            driver = webdriver.PhantomJS('C:/Program Files/phantomjs-2.1.1-windows/bin/phantomjs.exe')
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html)
        except:
            print("Error loading FOs file:", exc_info()[0])
            raise
        return soup

    def rip_fos(self, soup):
        try:
            lis = soup.find_all('li', {'class': 'portal-type-folder castle-grid-block-item'})
            for li in lis:
                h3_title = li.find('h3', {'class': 'title'})
                # Name
                fo_name = h3_title.find('a').get_text()
                # External URL
                fo_url_external = h3_title.find('a')['href']
                # Icon
                iconurl = li.find('div', {'class': 'focuspoint'})['data-base-url']
                iconfilepath = "../images/FOImages/" + fo_name.replace(" ", "") + '.jpg'

                # Download the image if we don't already have it
                if not path.isfile(iconfilepath):
                    sleep(10)
                    response = requests.get(iconurl, stream=True)
                    with open(iconfilepath, 'wb') as out_file:
                        copyfileobj(response.raw, out_file)
                    del response
                print(iconurl)

                desc_raw = soup.find('div', {'class': 'description'})
                fo_address = str(desc_raw.find_all('p')[0]).split('<br/>')[0].replace("<p>", "") + ', ' + \
                             str(desc_raw.find_all('p')[0]).split('<br/>')[1]
                # Address

        except:
            print("Error ripping FOs file:", exc_info()[0])
            raise

    def upload_fos(self, fos):
        for fo in fos:
            strSQL = "INSERT INTO [Published_FO] " \
                     "( [FOName], [IconFilepath], [FOURL], [FOLat], [FOLong] ) " \
                     "VALUES " \
                     "( ?, ?, ?, ?, ? );"
            params = []
            params = [fo.FOName, fo.IconFilepath, fo.FOURL, fo.FOLat, fo.FOLong]
            FOID = self.sql.insert_get_id(strSQL, params)
            fo.ProfileID = FOID

        strSQL2 = "UPDATE [Published_FO] " \
                  "SET [FOName] = LEFT([FOName], CHARINDEX(',', [FOName]) - 1) " \
                  "WHERE CHARINDEX(',', [FOName]) > 0;"
        self.sql.run_query(strSQL2)

    def rip_foleaders(self, fos):
        browser = webdriver.Firefox()
        leadertext = ""
        for fo in fos:
            browser.get(fo.FOURL)
            print('Loading:', fo.FOURL)
            soup = BeautifulSoup(browser.page_source)
            leader = soup.find('div', {'class': 'portletContent'}).find_all('table')[3].get_text().strip()
            try:
                subsraw = soup.find('div', {'class': 'portletContent'}).find_all('table')[4]
                substd = subsraw.find_all('td')
            except:
                substd = ""

            subs = ""
            for td in substd:
                subs = subs + td.get_text() + "; "

            remap = {
                ord('\t'): ' ',
                ord('\f'): ' ',
                ord('\r'): None,
                ord('\n'): None
            }

            leadertext = leadertext + "[" + fo.FOName + "]: "
            leader = leader.translate(remap)
            leadertext = leadertext + leader + '\n'
            subs = subs.translate(remap)
            leadertext = leadertext + subs + '\n'
            print(leader)
            print(subs)
            sleep(5)

        with open('LeadershipRaw.txt', 'w') as f:
            f.truncate()
            f.write(leadertext)
        f.closed
        # try:
        #     leader_title = content.find('td', {'class': ['blackgraphtx', 'greygraphtx']}).find('strong').get_text()
        #     leader_name = content.find('td', {'class': ['blackgraphtx', 'greygraphtx']}).find('a').get_text()
        # except:
        #     try:
        #         leader_title = content.find('p', {'class': ['blackgraphtx', 'greygraphtx']}).find('strong').get_text()
        #         leader_name = content.find('p', {'class': ['blackgraphtx', 'greygraphtx']}).find('a').get_text()
        #     except:
        #         try:
        #             leader_title = content.find('td', {'class': ['blackgraphtx', 'greygraphtx']}).find('b').get_text()
        #             leader_name = content.find('td', {'class': ['blackgraphtx', 'greygraphtx']}).find('a').get_text()
        #         except:
        #             try:
        #                 leader_title = content.find('td', {'class': ['blackgraphtx', 'greygraphtx']}).find('b').get_text()
        #                 leader_name = content.find('td', {'class': ['blackgraphtx', 'greygraphtx']}).find('span').get_text()
        #             except:
        #                 try:
        #                     leader_title = content.find('span', {'class': ['blackgraphtx', 'greygraphtx']}).find('strong').get_text()
        #                     leader_name = content.find('span', {'class': ['blackgraphtx', 'greygraphtx']}).find('a').get_text()
        #                 except:
        #                     try:
        #                         leader_title = content.find_all('span', {'class': ['blackgraphtx', 'greygraphtx']})[0].get_text()
        #                         leader_name = content.find_all('span', {'class': ['blackgraphtx', 'greygraphtx']})[1].get_text()
        #                     except:
        #                         leader_title = "None"
        #                         leader_name = "None"

    def upload_foleaders(self, fos):
        with open('LeadershipRaw.txt', 'r') as f:
            sql = SqlTlkt()
            for line in f:
                # if header then get foname and query foid and get leader and leadername
                fn = ""
                ltitle = ""
                lname = ""
                if len(line) > 0:
                    if line.find('[') >= 0:
                        if len((line.split('['))[1].split(']')[0]) > 0:
                            fn = (line.split('['))[1].split(']')[0]
                            if line.find('Special Agent in Charge') > 0:
                                ltitle = 'Special Agent in Charge'
                                lname = line[line.find('Special Agent in Charge')+len('Special Agent in Charge'):].strip()
                            elif line.find('Assistant Director in Charge'):
                                ltitle = 'Assistant Director in Charge'
                                lname = line[line.find('Assistant Director in Charge')+len('Assistant Director in Charge'):].strip()
                            else:
                                ltitle = "<?>"
                                lname = '<?>'
                        print(fn + "-->", ltitle+":", lname)
                        # Get the FOID
                        strSQL = "SELECT [id] FROM [Published_FO] WHERE [FOName] = ?"
                        params = []
                        params = [fn]
                        foid = sql.get_sql_list(strSQL, params)[0][0]
                        # Insert the Leader
                        strSQL2 = "INSERT INTO [Published_FOLeadership] " \
                                  "( [FOProfileID], [FullName], [Title], [isLead] ) " \
                                  "VALUES " \
                                  "( ?, ?, ?, ? );"
                        params2 = []
                        params2 = [foid, lname, ltitle, 1]
                        sql.run_query(strSQL2, params2)
                    else:
                        # Try to parse titles and names... ugh
                        chunks = line.strip().split(';')
                        if len(chunks[0]) > 0:
                            ltitle = chunks[0].strip()
                            dudes = chunks[1].strip().split('-')
                            for dude in dudes:
                                if len(dude) > 0:
                                    lname = dude.strip()
                                    print(ltitle+":", lname)
                                    strSQL = "INSERT INTO [Published_FOLeadership] " \
                                             "( [FOProfileID], [FullName], [Title], [isLead] ) " \
                                             "VALUES " \
                                             "( ?, ?, ?, ? );"
                                    params = []
                                    params = [foid, lname, ltitle, 0]
                                    sql.run_query(strSQL, params)
        f.closed
