import urllib.parse

token = 'TOKEN'
username = urllib.parse.quote_plus('DBUSERNAME')
password = urllib.parse.quote_plus('DBPASSWORD')

dbURI = "DBURI"
dbNAME = 'DBNAME'
sleep_duration = 5*60 #seconds
prune_period = 30*60 #seconds
page_size_max = 1000000 #bytes
log_channel = 717840269654884462