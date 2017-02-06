from sys import argv
from LoadFO import *


if __name__ == '__main__':
    fo_url = argv[1]
    db_addr = argv[2]
    db = argv[3]
    db_port = argv[4]
    db_user = argv[5]
    db_pwd = argv[6]
    key = argv[7]

    if fo_url:
        lfo = LoadFO(db_addr, db, db_port, db_user, db_pwd, key)
        fo_soup = lfo.get_soup(fo_url)
        [ripped_fo_data, ripped_fo_leads] = lfo.rip_fos(fo_soup)
        # lfo.upload_fos(ripped_fo_data)
        # lfo.upload_fo_leaders(ripped_fo_leads)
    print('Done!, ["Hip", "Hip"]!')
