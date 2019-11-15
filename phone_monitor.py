#!/usr/bin/env python3

""" Developed by Valentyna Fihurska for HireRush.com
	Start of development: 18-Oct-2019
	The program is created with HireRush`s problem in mind, namely
	significant percentage of blocked messages due to 30007 error.
	Credit for help with twilio API goes to Alex Sheplyakov.
	
"""

# +13472529810
# +18185325348
# +19157773224

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
import sqlite3

file = open('tokens.txt', 'r')
tokens = file.readlines()


ACCOUNT_SID = tokens[0].strip()
AUTH_TOKEN = tokens[1].strip()
SMS_SERVICE_SID = tokens[2].strip()


def fill_data_base(frame):
# Automatic filling the data base with scraped information

	connection = sqlite3.connect('./for_hirerush.db')
	cursor = connection.cursor()
	try:
		cursor.execute('CREATE TABLE phone_monitor_2days_stats_2min_interval (banned INT, date_time TEXT, partial_load DECIMAL, percentage_banned DECIMAL, phone TEXT, total INT)')
	except Exception as e:
		pass
	cursor.execute("INSERT INTO phone_monitor_2days_stats_2min_interval VALUES (?, ?, ?, ?, ?, ?)", 
		(int(frame['banned']), str(frame['date']), float(frame['partial_load']), float(frame['percentage_banned']), str(frame['phone']), int(frame['total'])))
	connection.commit()
	cursor.close()
	connection.close()




#'https://preview.twilio.com/Numbers/ActiveNumbers/{}.json'
def check_status(now=datetime.now()):
	""" The function mostly should be credited to Alex Sheplyakov. My own contribution is in 
		extending the functionality to remove number from service if banned numbers` 
		percentage (due to 30007 error) exceeds 25 % from total number of sent messages
		and logging tooling for further analycis. """

	lock = threading.Lock()
	client = Client(ACCOUNT_SID, AUTH_TOKEN)
	#today = datetime.now()

	period = timedelta(days=2)
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
		fill_data_base(phone_seria)
		#print(phone_frame)
		#print(phone, "\t", phones_map[phone]['total'], "\t", phones_map[phone]['ban'], (phones_map[phone]['ban']/phones_map[phone]['total'])*100, "\t", partial_load)
		#time.sleep(10)
		if int(phones_map[phone]['total']) < 25:
			pass
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
	#phone_frame.to_csv('full_phone_log_3_days_stats.csv', mode='a', header=False)
	#fill_data_base(phone_frame)
	try:
		print(phone_frame.head(15))
	except Exception:
		print(phone_frame)


if __name__ == '__main__':
	while True:
		check_status(datetime.now())
		time.sleep(120)
		if (time.localtime().tm_hour > 2) and (time.localtime().tm_hour < 13):
			time.sleep(43000)
