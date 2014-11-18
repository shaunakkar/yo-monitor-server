'''
Created on Oct 28, 2014

@author: shaunak.kar

WARN :: Requires/Contains Confidential Information: Please add/remove Google
App Password and Yo API Key.
'''
__author__ = 'shaunak.kar'

import requests
import smtplib
import time
import csv
from sched import scheduler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
class Monitor_CSG():
    def __init__(self):
    
        print ('*******Monitoring ABC Servers*********')
        print ('Initialising....')
        self.logs = []
        
    
    def execute_monitor(self, start, end, pulse, func):
        '''
        
        Scheduler runs from here. This is the entry point of the script
        
        '''
        
        s = scheduler(time.time, time.sleep)
        scan_begin = start
        while scan_begin <= end:
            s.enterabs(scan_begin, 0, func, ())
            scan_begin += pulse
        print ('Starting Monitor at ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        s.run()
        self.create_csv()
        print('\nEnding Monitor  at ', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    
    def check_heartbeat(self):
        ''' 
        
        Checks Heartbeat and includes core monitor logic
        
        '''
        
        print('\nChecking Heartbeat @ ', time.strftime('%H:%M:%S', time.localtime()))
        url = ''
        r = requests.get(url)
        r_json = r.json()
        print (len(r_json))
        if 1 and len(r_json)<4: # Tweak
            print('At least One Server Down...')
            self.send_alert()
            return
        #Reading api response as json
        les_5 = r.json()[0]['recentPauseTimePercent']
        les_6 = r.json()[2]['recentPauseTimePercent']
        ls_5 = r.json()[3]['recentPauseTimePercent']
        ls_6 = r.json()[1]['recentPauseTimePercent']
        # Formatting for CSV
        les_5.insert(0, 'LES5')
        les_6.insert(0, 'LES6')
        ls_5.insert(0, 'LS5')
        ls_6.insert(0, 'LS6')
        self.logs.append([les_5, les_6, ls_5, ls_6])
                
        if r.status_code == 200:
            if 1 and any(True for a in ls_6[1:]+ls_5[1:] if a>35 ): # Tweak || Removing format created for CSV temporarily
                self.create_csv()
                print('Sending Alert...')
                self.send_alert()
            print('Heartbeat Recorded..')
        else:
            print('WARN: Error reading API ')
        
    def create_csv(self):
        ''' 
        
        Creates CSV of heartbeat logs in the current folder
        
        '''
        with open('ABC_Monitor_logs.csv', 'w', newline='') as csv_logs:
            shakespeare = csv.writer(csv_logs, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            for i, l in enumerate(self.logs):
                shakespeare.writerow(['Cycle : {0}'.format(i + 1)])
                shakespeare.writerows(l)

    def send_alert(self):
        
        '''
        
        Sends a mail/yo to the specified user from gmail and Yo! servers
        
        '''
        try:
            self.yo_alert()
        except:
            print('Something went wrong while sending a Yo')
            return False
            
        if 0:
            from_addr = 'shaunak88@gmail.com'
            to_addrs = 'shaunak.kar@liquidanalytics.com'
            msg=MIMEMultipart()
            msg['Subject'] = 'ABC Monitoring Alert LS5/LS6'
            msg.attach(MIMEText('Houston We have a problem!'))
            print(msg)
        
            # Credentials for gmail might include app specific passwords.
            username = 'shaunak88@gmail.com'
            password = ''  # Not your email password: this is an app pasword managed by gmail. Ping me for details.
            try:
                # Send email(might land in the junk folder)
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.starttls()
                server.login(username, password)
                server.sendmail(from_addr, to_addrs, msg.as_string())
                server.quit()
            except:
                print('Something went wrong while sending an email')
                pass
                    
                
    def yo_alert(self, send='user'):
        
        ''' 
        
        Sends a notification to specified user on his mobile
        
        '''
        if send == 'user':
            username = ''
            youser_data = {"api_token": '',
                            "username": username, }
            youser_url = "http://api.justyo.co/yo/"
            youser = requests.post(youser_url, data=youser_data)
            if youser.status_code == 200:
                return True
            else:
                print('Yo Alert Failed')
        
        elif send == 'all':
            yoall_data = {"api_token": '',
                            }
            yoall_url = "http://api.justyo.co/yoall/"
            yoall = requests.post(yoall_url, data=yoall_data)
            if yoall.status_code == 201:
                return True
            else:
                while yoall.status_code != 201:
                    time.sleep(10) #Only required for demo. Consecutive Yo's might be discarded.
                    yoall = requests.post(yoall_url, data=yoall_data)
                    
            
if __name__ == '__main__':
    o = Monitor_CSG()
#     Next line is for real-time monitor. The one after is testing.
    o.execute_monitor(time.time()+5, time.time()+(60*60*2), 120, o.check_heartbeat )
#    o.execute_monitor(time.time() + 1, time.time() + 10, 5, o.check_heartbeat)
