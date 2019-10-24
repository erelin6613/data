#!/usr/bin/env python3

""" Developed by Valentyna Fihurska
	Start of development: 18-Oct-2019
	The program is created with HireRush`s problem in mind, namely
	significant percentage of blocked messages due to 30007 error.
	Credit for help with twilio API goes to Alex Sheplyakov.
	
"""

import csv
import threading
from queue import Queue
from twilio.rest import Client
from datetime import date, datetime, timedelta
import os
import json
import smtplib
import requests
#import logging
import time
import pandas as pd

ACCOUNT_SID = 'AC8d84a772e99693a91a7eb41d19d0df07'
AUTH_TOKEN = '38e2cd1a6d6e6d357eb528e0d3db011f'
SMS_SERVICE_SID = 'MG39504f8faa6db7238a80b7b8d5736164'

#'https://preview.twilio.com/Numbers/ActiveNumbers/{}.json'
def check_status(now=datetime.now()):
	""" The function mostly should be credited to Alex Sheplyakov. My own contribution is in 
		extending the functionality to remove number from service if banned numbers` 
		percentage (due to 30007 error) exceeds 25 % from total number of sent messages
		and logging tooling for further analycis. """

	lock = threading.Lock()
	client = Client(ACCOUNT_SID, AUTH_TOKEN)
	#today = datetime.now()

	period = timedelta(days=1)
	interval = now-period

	print(interval)

	errors = 0
	delivered = 0
	errors_30007 = 0
	total = 0
	phones_map = {}
	auth = (ACCOUNT_SID, AUTH_TOKEN) 
	r = requests.get('https://messaging.twilio.com/v1/Services/{}/PhoneNumbers'.format(SMS_SERVICE_SID), auth=auth)
	phones_dicts = json.loads(r.text)['phone_numbers']
	for message in client.messages.list(date_sent_after=interval):
		if phones_map.get(message.from_) == None:
			phones_map[message.from_] = {"total": 0, "ban": 0, "undeliv": 0}
		total += 1
		phones_map[message.from_]['total'] += 1
		if message.status == "delivered":
			delivered += 1
		else:
			phones_map[message.from_]["undeliv"] += 1;
			if message.error_code == 30007:
				phones_map[message.from_]['ban'] += 1
				errors_30007 += 1
			errors += 1

	fails_percent = (errors_30007 / total) * 100
	#print(phones_map)
	print(total)
	phone_seria = pd.Series()
	phone_frame = pd.DataFrame()
	for phone in phones_map.keys():
		#rel_percent = phones_map[phone]['total']/total
		#rel_percent_banned = (phones_map[phone]['ban']/phones_map[phone]['total']) * rel_percent
		partial_load = phones_map[phone]['total']/total
		phone_seria['phone'] = phone
		phone_seria['banned'] = int(phones_map[phone]['ban'])
		phone_seria['total'] = int(phones_map[phone]['total'])
		phone_seria['percentage_banned'] = (phones_map[phone]['ban']/phones_map[phone]['total'])*100
		phone_seria['partial_load'] = partial_load
		phone_seria['date'] = str(now)[0:19]
		phone_frame = phone_frame.append(phone_seria, ignore_index=True)
		
		#print(phone_frame)
		#print(phone, "\t", phones_map[phone]['total'], "\t", phones_map[phone]['ban'], (phones_map[phone]['ban']/phones_map[phone]['total'])*100, "\t", partial_load)
		#time.sleep(10)
		if partial_load < 0.09:
			continue
		else:
			if (phones_map[phone]['ban']/phones_map[phone]['total']) > 0.25:
				for ph in phones_dicts:
					if ph['phone_number'].strip() == phone.strip():
						phone_sid = ph['sid']
						client.messaging.services(SMS_SERVICE_SID).phone_numbers(phone_sid).delete()
						print('Phone', phone, 'deleted from SMS service')
						#logging.debug(log_string)
						with open('deleted_phones.csv', 'a') as file:
							file.write(phone+'\n')


	#data = {}
	frame = pd.Series()
	new_frame = pd.DataFrame()
	frame['banned_percent'] = fails_percent
	frame['date'] = now
	frame['delivered'] = delivered
	frame['error_30007'] = errors_30007
	frame['total_sent'] = total
	frame['undelivered'] = errors
	new_frame = new_frame.append(frame, ignore_index = True)
	new_frame.to_csv('phone_stats.csv', mode = 'a', header = False)
	phone_frame.to_csv('full_phone_log.csv', mode='a', header=False)
	try:
		print(phone_frame.head(13))
	except Exception:
		print(phone_frame)






def suspend_text_capability(phone_number):
	auth = (ACCOUNT_SID, AUTH_TOKEN)
	url = 'https://preview.twilio.com/Numbers/ActiveNumbers/{}.json'.format(phone_number.sid)
	
	json_str = """{
    				"items": [
        						{"phone_number": "{}",
            					"capabilities": {"voice": {"inbound_connectivity": true,
                    										"outbound_connectivity": true,
                    										"e911": true,
                    										"fax": true,
                    										"sip_trunking": true,
                    										"calls_per_second": 30,
                    										"concurrent_calls_limit": 30,
                    										"long_record_length": 30,
                    										"inbound_called_dtmf": true,
                    										"inbound_caller_dtmf": true,
                    										"inbound_caller_id_preservation": "international",
                    										"inbound_reachability": "global",
                    										"codecs": ["g711u"]
                    										},

                									"sms": {"inbound_connectivity": false,
                    										"outbound_connectivity": false,
                    										"gsm7": false,
                    										"ucs2": false,
                    										"gsm7_concatenation": false,
                    										"ucs2_concatenation": false,
                    										"inbound_sender_id_preservation": "international",
                    										"inbound_reachability": "global",
                    										"inbound_mps": -1
                    										},
                				
                									"mms": {"inbound_connectivity": false,
                    										"outbound_connectivity": false,
                    										"inbound_reachability": "global",
                    										"inbound_mps": -1
                    										}
            									}
								}]}""".format(phone_number)
	json_conf = json.loads(json_str)
	r = requests.post(url, auth=auth, data = json_conf)

if __name__ == '__main__':
	while True:
		check_status(datetime.now())
		time.sleep(120)
		if (time.localtime().tm_hour > 2) and (time.localtime().tm_hour < 14):
			time.sleep(43000)