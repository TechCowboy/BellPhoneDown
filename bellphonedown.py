#!/usr/bin/env python3
# Sept 8, 2021 12:00
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
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import re
import smtplib
import ssl
import getpass


port            = 465
smtp_server     = input("Type in your smtp url: ")
sender_email    = input("Type in your email address to send from: ")
sender_password = getpass.getpass("Type in your password: ")
receiver_email  = input("Type in your email address to send to: ")




 
# url to the Bell router

global_dynamicUrl = "http://192.168.2.1"

# we control chrome to get the webpage as a headless browser
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")
options.add_argument("start-maximized")
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

last_status = ""
minutes = 1

while(True):

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options
                              )


    # open the page with javascript available

    driver.execute_script("window.open('http://192.168.2.1', '_self')")

    # the page has a useless self promotion when starting, so wait for
    # the page to load
    print("Waiting for page to load...")
    time.sleep(10)
    print("Awake!")

    # the page should be here now
    pageSource = driver.page_source

    # parse the page and find the 3 services

    soup = BeautifulSoup(pageSource, "html.parser")
    data_internet = soup.find("div", id="internetContainer")
    data_tv = soup.find("div", id="fibeTvContainer")
    data_voice = soup.find("div", id="fibeVoiceContainer")

    pattern = r'status="(\w*)"'

    internet = "DOWN"
    tv       = "DOWN"
    phone    = "DOWN"

    # find out the status of each service
    status = re.search(pattern, str(data_internet))
    if status != None:
        internet = status.groups()[0].upper()
        print("Internet: " + status.groups()[0])

    status = re.search(pattern, str(data_tv))
    if status != None:
        tv = status.groups()[0].upper()
        print("TV: " + status.groups()[0])

    status = re.search(pattern, str(data_voice))
    if status != None:
        phone = status.groups()[0].upper()
        print("Phone: " + status.groups()[0])

    status = [internet, tv, phone]

    if "NOTSUBSCRIBED" in status:
        if last_status != status:
            print("Sending Email!")
            
            subject = 'Bell Service Interruption!'
            body = "\nInternet: " + internet + "\nTV:       " + tv + "\nPhone:    " + phone + "\n"

            email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sender_email, ", " +receiver_email, subject, body)

            print(email_text)
            
            try:
                server = smtplib.SMTP_SSL(smtp_server, port)
                server.ehlo()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, email_text)
                server.close()

                print('Email sent!')
            except Exception as e:
                print(f'Something went wrong sending email\n{str(e)}')

    last_status = status
    print("Sleeping...")
    time.sleep(60*minutes)
    driver.close()
    driver.quit()
