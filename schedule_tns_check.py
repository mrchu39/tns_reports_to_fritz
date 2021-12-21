import get_at_reports
import time
import datetime

get_at_reports.submit_tns_alerts(3)

num = 0

while(True):
    if datetime.datetime.utcnow().hour == 0 and num != 1:
        get_at_reports.submit_tns_alerts(3)
        first = 1

    if datetime.datetime.utcnow().hour == 12 and num != 2:
        get_at_reports.submit_tns_alerts(3)
        first == 2
        
    time.sleep(1)
