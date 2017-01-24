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
    google_api_key = argv[5]

    if fo_url:
        lfo = LoadFO(db, dbuser, dbpwd)
        fo_soup = lfo.download_fos(fo_url, google_api_key)
        lfo.rip_fos(fo_soup)

    print('Done!, ["Hip", "Hip"]!')
