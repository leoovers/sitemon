import argparse
import configparser
from datetime import datetime
from email.message import EmailMessage
import subprocess
import urllib.request
from urllib.error import URLError, HTTPError

TIMEOUT = 30

def parse_args():
    parser = argparse.ArgumentParser(
            prog='SiteMonitor',
            description='Monitor website status',
            epilog='lörs')

    parser.add_argument('-u', '--urls', nargs='+', required=True)
    parser.add_argument('-n', '--notify', action='store_true', default=False, required=False)
    args = parser.parse_args()
    print('Starting run at ', datetime.now())
    print('Requesting urls:', args.urls)
    return args

def parse_conf():
    config = configparser.ConfigParser()
    config.read('site_monitor.config')
    return config['EMAIL']

def site_status(url):
    try:
        status_code = urllib.request.urlopen(url, timeout=(TIMEOUT / 2)).getcode()
    except HTTPError as e:
        if e.code == 401:
            return (url, True)
        else:
            return (url, e.code)
    except URLError as e:
        return (url, e.reason.__str__())
    else:
        return (url, True)

def notify(errors, notify, conf):
    msg_body = ''
    for error in errors:
        msg_line = error[0] + " - " + error[1] + "\n"
        msg_body += msg_line

    print('Errors:')
    print(msg_body)

    if notify:
        msg = EmailMessage()
        msg.set_content(msg_body)
        msg['From'] = conf['From']
        msg['To'] = conf['To']
        msg['Subject'] = 'Website unavailable'
        subprocess.run(
            ["mail", "-s", "Website unavailable", conf['User']], 
            input=msg.as_string(), text=True, check=True)

if __name__ == "__main__":
    args = parse_args()
    email_conf = parse_conf()
    errors = []
    for url in args.urls:
        result = site_status(url)
        if result[1] != True:
            errors.append(result)
    if errors:
        notify(errors, args.notify, email_conf)
    else:
        print('No errors to report.', '\n')
    print('==============================================', '\n')
 

