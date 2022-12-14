#!/usr/bin/env python3
# Sept 8, 2021 21:00
# bellphonedown.py

# I found my phone service down 3 times
# even though my internet service remained up
#
# The phone service is an absolute requirement
# as I am taking care of my 97 year old mother
# and she/I need to be able to call 911
#
# Bell were unwilling to discuss how to at least
# let me know when the service is down so I could
# restart the router
#
# this python script lets you know when any
# of your subscribed services are down
# (provided you still have internet service)
# and emails you

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import time
from bs4 import BeautifulSoup
import re
import smtplib
import ssl
import getpass
import os


port            = 465   # number
smtp_server     = None  # string containing the server name
sender_email    = None  # email address to send to
sender_password = None  # your email password
receiver_email  = None  # who to send the email to

# if you don't want to type in your
# credentials each time, you can
# create a file called mailinfo.txt
# and put the assignments in that file
# example contents (don't include # symbol in file):
#
#port            = 578
#smtp_server     = "smtp.gmail.com"
#sender_email    = "from@domain.com"
#sender_password = "password"
#receiver_email  = "to@domain.com"

mailinfo = "mailinfo.txt"
if os.path.exists(mailinfo):

    with open(mailinfo) as f:
        lines = f.readlines()
        
    for line in lines:
        try:
            exec(line.strip())
        except Exception as e:
            print(str(e))
        
else:    

    port            = input("Type in smtp port number: ")
    port            = eval(port)
    smtp_server     = input("Type in your smtp url: ")
    sender_email    = input("Type in your email address to send from: ")
    sender_password = getpass.getpass("Type in your password: ")
    receiver_email  = input("Type in your email address to send to: ")

failure = "DOWN"
success = "UP"
 

options = Options()


last_status = ""

# Bell has an annoying intro that requires us to wait
# before the data is available. Number of seconds to wait.
delay_reading_page = 10

# frequency to check in minutes
minutes = 15

# on the first time, we want to send an email
# if there is a failure, otherwise send an
# email whenever a service status changes
first_time = True

# I've only tested Chrome, Edge, and Internet Explorer, however, other browsers are supported,
# but have not been tested

# Chrome

# optionally we can control chrome as a headless browser
options.headless = True
options.add_argument("--window-size=1920,1080")
options.add_argument("start-maximized")
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# Chromium
#driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))

# Brave
#driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))

# FireFox
#driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Edge
#driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))

# Internet Explorer
#driver = webdriver.Ie(service=Service(IEDriverManager().install()))

try:
    while(True):

        # open the page and evaluate the javascript as well
        driver.execute_script("window.open('http://home', '_self')")

        # the page has a useless self promotion when starting, so we need
        # to wait for the page to completely load
        print(f"Waiting {delay_reading_page} seconds for page to load...")
        time.sleep(delay_reading_page)
        
        # the page should be here now
        print("Getting page...")
        pageSource = driver.page_source

        # parse the page and find the 3 services
        soup = BeautifulSoup(pageSource, "html.parser")
        
        data_internet = soup.find("div", id="internetContainer")
        data_tv       = soup.find("div", id="fibeTvContainer")
        data_voice    = soup.find("div", id="fibeVoiceContainer")

        # use this search pattern to find out the current status
        pattern = r'status="(\w*)"'

        # clear any existing status
        internet = None
        tv       = None
        phone    = None

        # find out the status of each service
        status = re.search(pattern, str(data_internet))
        if status != None:
            internet = status.groups()[0].upper()
            print("Internet: " + status.groups()[0])
            no_internet = internet != success
        else:
            print("No internet status")
            no_internet = True

        status = re.search(pattern, str(data_tv))
        if status != None:
            tv = status.groups()[0].upper()
            print("      TV: " + status.groups()[0])
        else:
            print("No tv status")
            

        status = re.search(pattern, str(data_voice))
        if status != None:
            phone = status.groups()[0].upper()
            print("   Phone: " + status.groups()[0])
        else:
            print("No phone status")


        # no point in attempting to email if there is no internet
        if no_internet:
            print(f"Can't connect or can't determine current internet state")
        else:
            status = [internet, tv, phone]

            if first_time:
                last_status = status
                if failure in status:
                    # force an email to be sent if there is a failure on the
                    # first status check
                    last_status = "" 
            
            #print(status)
            
            # Everytime the status changes, send an email
            if last_status != status:
                last_status = status
                print("Sending Email!")
                
                subject = 'Bell Service Status Change!'
                body = "\nInternet: " + internet + "\nTV:       " + tv + "\nPhone:    " + phone + "\n"

                email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sender_email, ", " +receiver_email, subject, body)
                
                try:
                    server = smtplib.SMTP_SSL(smtp_server, port)
                    server.ehlo()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, email_text)
                    server.close()

                    print('Email sent!')
                except Exception as e:
                    print(f'Something went wrong sending email\n{str(e)}')

        # wait for a while and then check again
        remaining = 60 * minutes
        while remaining > 0:
            print(f"Next check in {remaining} seconds  ...\r", end='')
            time.sleep(1)
            remaining -= 1
except Exception as e:
    print("Error occured: "+ str(e))

print("Closing driver...")
driver.close()
print("Quit driver...")

driver.quit()
print("Done.")