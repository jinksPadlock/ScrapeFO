from LoadFO import *


# Load FOs
# Instantiate Loader
lfo = LoadFO()
# Load FOs
fos = lfo.LoadFOsFromDDFile()
# Upload FOs to FB
lfo.upload_fos(fos)
# Scrape current Leadership
lfo.rip_foleaders(fos)
# Upload Ripped content to DB
lfo.upload_foleaders(fos)

print('Done!, ["Hip", "Hip"]!')
