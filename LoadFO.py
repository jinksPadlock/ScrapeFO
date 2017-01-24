import sys
from bs4 import BeautifulSoup
import os.path
import shutil
import requests
from FO import *
from SqlTlkt import *
import time
from selenium import webdriver


class LoadFO:
    def __init__(self):
        self.Success = False

    def LoadFOsFromDDFile(self):
        try:
            # Load soup for RepNo
            dd_filepath = './FOData/FO_field.html'
            rs_f = open(dd_filepath, 'r', encoding='utf-8')
            soup = BeautifulSoup(rs_f)
            print("Loading XML file:", dd_filepath)
        except:
            print("Error loading XML file:", sys.exc_info()[0])
            raise

        fos = soup.find_all('dt')
        fotabs = soup.find_all('dd', {"class": "tab"})
        fogeos = soup.find_all('dd', {"class": "geo"})
        folayers = soup.find_all('dd', {"class": "layers"})

        fo_all = []

        for i in range(56):
            a = fos[i].find('a')
            foname = a.get_text()
            print(i+1, foname)
            iconurl = fotabs[i].find('img')['src']
            iconfilepath = "../images/FOImages/" + iconurl.rsplit('/', 1)[1]
            # Download the image if we don't already have it
            if not os.path.isfile(iconfilepath):
                time.sleep(10)
                response = requests.get(iconurl, stream=True)
                with open(iconfilepath, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
            print(iconurl)

            try:
                blurb = fotabs[i].find('span', {"class": "blackgraphtx"})
                fourl = blurb.find('a', {"class": "internal-link"})['href']
                blurbsplit = "".join([s for s in (blurb.get_text()).strip().splitlines(True) if s.strip()])
            except AttributeError as err:
                blurb = fotabs[i].find('p', {"class": "blackgraphtx"})
                fourl = blurb.find('a', {"class": "internal-link"})['href']
                blurbsplit = "".join([s for s in (blurb.get_text()).strip().splitlines(True) if s.strip()])

            folat = fogeos[i].find('span', {'class': 'latitude'}).get_text()
            folong = fogeos[i].find('span', {'class': 'longitude'}).get_text()

            fo = FieldOffice(foname, iconfilepath, fourl, folat, folong)
            fo_all.append(fo)

        return fo_all

    def upload_fos(self, fos):
        sql = SqlTlkt()
        for fo in fos:
            strSQL = "INSERT INTO [Published_FO] " \
                     "( [FOName], [IconFilepath], [FOURL], [FOLat], [FOLong] ) " \
                     "VALUES " \
                     "( ?, ?, ?, ?, ? );"
            params = []
            params = [fo.FOName, fo.IconFilepath, fo.FOURL, fo.FOLat, fo.FOLong]
            FOID = sql.insert_get_id(strSQL, params)
            fo.ProfileID = FOID

        strSQL2 = "UPDATE [Published_FO] " \
                  "SET [FOName] = LEFT([FOName], CHARINDEX(',', [FOName]) - 1) " \
                  "WHERE CHARINDEX(',', [FOName]) > 0;"
        sql.run_query(strSQL2)

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
            time.sleep(5)

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
