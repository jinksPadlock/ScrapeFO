from sys import argv
from LoadFO import *


# # Load FOs
# # Instantiate Loader
# lfo = LoadFO()
# # Load FOs
# fos = lfo.LoadFOsFromDDFile()
# # Upload FOs to FB
# lfo.upload_fos(fos)
# # Scrape current Leadership
# lfo.rip_foleaders(fos)
# # Upload Ripped content to DB
# lfo.upload_foleaders(fos)


if __name__ == '__main__':
    fo_url = argv[1]
    db = argv[2]
    dbuser = argv[3]
    dbpwd = argv[4]
    key = argv[5]

    if fo_url:
        lfo = LoadFO(db, dbuser, dbpwd, key)
        fo_soup = lfo.get_soup(fo_url)
        [ripped_fo_data, ripped_fo_leads] = lfo.rip_fos(fo_soup)
        # lfo.upload_fos(ripped_fo_data)
        # lfo.upload_foleaders(ripped_fo_leads)
    print('Done!, ["Hip", "Hip"]!')
