from sys import argv
from LoadFO import *


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
        # lfo.upload_fo_leaders(ripped_fo_leads)
    print('Done!, ["Hip", "Hip"]!')
