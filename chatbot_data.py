#!/usr/bin/env python3

"""
The algorithm for extracting the sent/received email by support team
using Google Mail API
"""

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from time import sleep
import time
import base64
import email
import json
from datetime import datetime
import sqlite3
import re
import gensim 
#import findspark
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.types import StructType, StructField, StringType
import pyspark

#schema = StructType([StructField('date_time', StringType(), True),
#                     StructField('sender', StringType(), True),
#                     StructField('receiver', StringType(), True),
#                     StructField('history_id', StringType(), True),
#                     StructField('id', StringType(), True),
#                     StructField('snippet', StringType(), True),
#                     StructField('response_id', StringType(), True),
#                     StructField('message', StringType(), True)])


#data = pd.read_csv('chatbot_data.csv')
#data.set_index('id')
#print(data.head(10))

def load_data(db_path, table_name):

	connection = sqlite3.connect(db_path)
	cursor = connection.cursor()	
	cursor.execute('SELECT * FROM {}'.format(table_name))

def spellcheck(data_path):
	pass
	#model = gensim.models.KeyedVectors.load_word2vec_format('/home/val/GoogleNews-vectors-negative300.bin.gz')
	#print(model.index2word)


def clean_messages(frame):

#for col, row in data.iterrows():
	msg = frame['message'].strip('\n').strip('\r')
	try:
		frame['message'] = msg.split('Client IP')[0].split('Message:')[1].strip()
	except Exception as e:
		#print(e)
		try:
			frame['message'] = msg.split('Content-Type:')[1].split('--__swift')[0].split('\n')[1:].strip()
		except Exception as e:
			frame['message'] = msg
			pass
	if '=E2=80=99' in frame['message']:
		frame['message'] = frame['message'].replace('=E2=80=99', '')

	if '=' in frame['message']:
		frame['message'] = frame['message'].replace('=', '')

	try:
		frame['message'] = frame['message'].replace('\n', ' ')
	except Exception:
		pass

	try:
		frame['message'] = frame['message'].replace('\r', ' ')
	except Exception:
		pass

	try:
		frame['message'] = frame['message'].replace('\t', ' ')
	except Exception:
		pass

	return frame

	#sleep(5)



def fill_base(frame):
# Automatic filling the data base with scraped information

	connection = sqlite3.connect('./for_hirerush.db')
	cursor = connection.cursor()
	try:
		cursor.execute('CREATE TABLE chatbot_data (date_time TEXT, sender TEXT, receiver TEXT, history_id TEXT, id TEXT, snippet TEXT, response_id TEXT, message TEXT, intent TEXT)')
	except Exception as e:
		pass
	cursor.execute("INSERT INTO chatbot_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
		(str(frame['date_time']), frame['sender'], str(frame['receiver']), str(frame['history_id']), str(frame['id']), str(frame['snippet']), str(frame['response_id']), str(frame['message']), str(frame['intent'])))
	connection.commit()
	cursor.close()
	connection.close()



def get_gmail_data():

	frame = pd.Series()
	email_pattern = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
	SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
	flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
	creds = flow.run_local_server(port=0)
	service = build('gmail', 'v1', credentials=creds)
	#all_labels = ['in:QandA', 'in:blog', 'in:marketing']

		#for label in all_labels:
	request = service.users().messages().list(userId='me', q='in:QandA')
	while request is not None:

			response = request.execute()
			#print(response)
			for each in response['messages']:
				msg = service.users().messages().get(userId='me', id=each['id'], format='full').execute()
				raw_msg = service.users().messages().get(userId='me', id=each['id'], format='raw').execute()
				message = base64.urlsafe_b64decode(raw_msg['raw'].encode('ASCII'))
				frame['history_id'] = msg['historyId']
				frame['id'] = msg['id']
				frame['date_time'] = datetime.fromtimestamp(int(msg['internalDate'])/1000)
				frame['response_id'] = None
				frame['intent'] = 'blog'
				#print(msg,'\n\n')
					#
					# dict_keys(['id', 'threadId', 'labelIds', 'snippet', 'historyId', 'internalDate', 'sizeEstimate', 'raw'])
					#msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
					#try:
				#print(msg['labelIds'])
				for header in msg['payload']['headers']:
					if 'X-Spam-Checked-In-Group' in header['name'] \
					or 'Delivered-To' in header['name']:
						frame['receiver'] = header['value'].strip('\n').strip('\r')
					if 'From' in header['name']:
						frame['sender'] = header['value'].strip('\n').strip('\r')
				
				frame['snippet'] = raw_msg['snippet']
				try:
					frame['message'] = message.decode().split('Content-Transfer-Encoding: quoted-printable')[1].strip('\n').strip('\r')
				except Exception:
					frame['message'] = message.decode().strip('\n').strip('\r')
				frame = clean_messages(frame)
				fill_base(frame)
				print(frame)
				#print(frame['message'])
				#exit()


			request = service.users().messages().list_next(previous_request=request,previous_response=response)
			#print('end of the loop')
				#sleep(5)

if __name__ == '__main__':
	frame = pd.read_csv('chatbot_data.csv', sep='\n')
	data = pd.DataFrame(columns= frame.columns[0].split(';'))
	for row in frame.iterrows():
		print(row[1]['date_time;sender;receiver;history_id;id;snippet;response_id;message;intent'])
		break
		#data.append(row.split(';'), ignore_index=True)
	print(data)
	#print(data.head(10))

	#get_gmail_data()

	#data = pd.read_csv('chatbot_data.csv', sep='\|')
	#data.set_index('id')
	#print(data.head(10))
	#data = data.apply(clean_messages)
	#print(data['message'].strip('\n').strip('\r'))
	#spark = SparkSession.builder.appName("chatbot_data").getOrCreate()
	#full_data = spark.read.csv('chatbot_data.csv', header=True, sep='\n')
	#print(full_data.show(10))


"""java_dir = '/usr/lib/jvm/java-11-openjdk-amd64'
	spark_dir = '/home/val/spark-3.0.0-preview-bin-hadoop3.2'
	os.environ['JAVA_HOME'] = java_dir
findspark.init(spark_home=spark_dir) """
	
#schema = StructType([])
#empty = pyspark.SparkContext.emptyRDD()

	#full_data = full_data.toPandas()
	#full_data = spark.createDataFrame(data, schema=schema)
#print(full_data.show())
#exit()
	#load_data('./for_hirerush.db')
	#spellcheck()
	#get_gmail_data()


"""
{'id': '16e6ad9983cfdfa8', 
'threadId': '16e6ad9983cfdfa8', 
'labelIds': ['IMPORTANT', 'Label_9181604431186176969', 'CATEGORY_PERSONAL'], 
'snippet': 'Name: Quotes Email: pnoflin@aol.com Subject: General enquiries Message: I gave a quote yesterday for a job that I did not get. I would like to have that quote back please. Client IP: 107.77.229.36,', 
'historyId': '6134250', 
'internalDate': '1573750673000', 
'payload': {'partId': '', 
			'mimeType': 'multipart/alternative', 
			'filename': '', 
			'headers': [0{'name': 'Delivered-To', 'value': 'val@hirerush.com'}, 
						1{'name': 'Received', 'value': 'by 2002:a0c:87a9:0:0:0:0:0 with SMTP id 38csp954218qvj;        Thu, 14 Nov 2019 08:57:55 -0800 (PST)'}, 
						2{'name': 'X-Received', 'value': 'by 2002:a9d:4c13:: with SMTP id l19mr7573775otf.269.1573750675473;        Thu, 14 Nov 2019 08:57:55 -0800 (PST)'}, 
						3{'name': 'ARC-Seal', 'value': 'i=3; a=rsa-sha256; t=1573750675; cv=pass;        d=google.com; s=arc-20160816;        b=IDaKAU0kZ+JEgGdo588egg4PMHdaR3T8l8/VwIMy9C/op0x7zUiaZlDv02kYU7mkts         w+2YmcUXFp3eDyFCU/UOt0OhHS+5PzULdm0LVW1N9HGSh1IbBhY+oYQQPU7IfESz6r8/         1BCnyEQ1DxmGVI/PE+t2QihOob2JYa5AfzUBpC6xvJQnP5Tzx3kUo7jtBi/HqmhP+zE1         Of/d1GJiVS7p7bg7oQfoImeT24i89F8Ov2CFNfBhIegjmpvSyd0/j2SVODQU2cdqQUN8         UmGXRd2i5sJlbwJZDfp0BvSpnMfZ8YmUSQHh8cgwMs5pXsWVSfQRSzoACU5UAjmUjFDJ         JkyQ=='}, 
						4{'name': 'ARC-Message-Signature', 'value': 'i=3; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;        h=list-unsubscribe:list-subscribe:list-archive:list-help:list-post         :list-id:mailing-list:precedence:mime-version:to:subject:date         :message-id:from:dkim-signature;        bh=mXG1kkxNIjJ5UVoi8yJbhMIDnA0rJ9I/3zkeiOwVRTc=;        b=DnjCw6MElbVucgcXxbLXKomDM2hpegn2zBYXIkMzNBzjkTM/7KoObCnVSC9X3rRHB6         OKN97DIAt+JdERCUEdTut5SSphxR+TZDss2AHXQyxefJqa5vO0E7AfivnXfDXoWi84A7         L4l8zfs7LK93QEpHKBPcyK1SWDJ5KhfzXjshbzxhurlKTiKoSN5r0HUoAm2fENq5Co7N         4qo3TfF1hvSUe7z71eLHtLDeHNrFOUBl4IHL1noe+wppQD1oxgZpQDCkeulQpmb+SXuW         HGGg/ACf/j89MAzj/OARUL+YHIcQo3vMzPlkESMeoGleVI6kZ8DQIXt8lKcKMfeEeO5X         Nt2g=='}, 
						5{'name': 'ARC-Authentication-Results', 'value': 'i=3; mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=Gg8OFFER;       arc=pass (i=2 spf=pass spfdomain=hirerush.com dkim=pass dkdomain=hirerush-com.20150623.gappssmtp.com);       spf=pass (google.com: domain of support+bncbdz3r57izyprbe4pw3xakgqewxhw7oa@hirerush.com designates 209.85.220.69 as permitted sender) smtp.mailfrom=support+bncBDZ3R57IZYPRBE4PW3XAKGQEWXHW7OA@hirerush.com'}, 
						6{'name': 'Return-Path', 'value': '<support+bncBDZ3R57IZYPRBE4PW3XAKGQEWXHW7OA@hirerush.com>'}, 
						7{'name': 'Received', 'value': 'from mail-sor-f69.google.com (mail-sor-f69.google.com. [209.85.220.69])        by mx.google.com with SMTPS id v22sor3662860oiv.22.2019.11.14.08.57.55        for <val@hirerush.com>        (Google Transport Security);        Thu, 14 Nov 2019 08:57:55 -0800 (PST)'}, 
						8{'name': 'Received-SPF', 'value': 'pass (google.com: domain of support+bncbdz3r57izyprbe4pw3xakgqewxhw7oa@hirerush.com designates 209.85.220.69 as permitted sender) client-ip=209.85.220.69;'}, 
						9{'name': 'Authentication-Results', 'value': 'mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=Gg8OFFER;       arc=pass (i=2 spf=pass spfdomain=hirerush.com dkim=pass dkdomain=hirerush-com.20150623.gappssmtp.com);       spf=pass (google.com: domain of support+bncbdz3r57izyprbe4pw3xakgqewxhw7oa@hirerush.com designates 209.85.220.69 as permitted sender) smtp.mailfrom=support+bncBDZ3R57IZYPRBE4PW3XAKGQEWXHW7OA@hirerush.com'}, 
						10{'name': 'ARC-Seal', 'value': 'i=2; a=rsa-sha256; t=1573750675; cv=pass;        d=google.com; s=arc-20160816;        b=igefAnmetYJsOFqIslq89LThtOCbMK7HrTSeozRXqFNVar9B94P2NBgQE+VvB/RwFs         bogD4MN7YSrVIy7w8qULyuZxQhgFQ3QhAgbUCiekToevko69g2/VCwgm4RtyLmT8y4cu         62gAdQDEdlkQU3791AN1R90dmarWFvF3MSRa8yPn9OfO34bRxBqbMlSlf4tcgrp2SyeF         sk28jrHuMvFr1k9qoHYvwCK868J9B+Nusb692oWI2sGYX0LVRihfS9cWvVSnCEkyY+ic         gXKJQqT5RJFbAN1t7fhEG353G91g0obeG6Q6UEpGIeVtyl/YZ8Fy6DHzHezyvjqL6HDL         47nA=='}, 
						11{'name': 'ARC-Message-Signature', 'value': 'i=2; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;        h=list-unsubscribe:list-subscribe:list-archive:list-help:list-post         :list-id:mailing-list:precedence:mime-version:to:subject:date         :message-id:from:dkim-signature;        bh=mXG1kkxNIjJ5UVoi8yJbhMIDnA0rJ9I/3zkeiOwVRTc=;        b=SDbd0mlxuUK32USUDet5JgoIEiTvM7DsMq87MoUFOAVDTfSPzdc6vlnXugqkhXVRMu         nnhOCx0FQ+y+dysTpiOCVwYLIdtsuYYOGywsvjsRraTSu4TLSSLpM8C5rhA9zDgItdSX         o/C7+zugBSuqqMKbO1pMqBKWRg9m8X8xZwzXkC4LKIAjG/TbSuFaELIopyyLfJ81LAwk         nGvWY0KilHFnBlCiAQjdpc2sDiTw9qrTuEP24W/pUxeHAwxEXsxOFAIAui/RkjpvGv/W         A7gRHQnPBt2IC5QV5TNGoCWReIVa8haazjj1zE3wE8XHWiUdKmdQbRuzsjyO85VmiPAW         GN6A=='}, 
						12{'name': 'ARC-Authentication-Results', 'value': 'i=2; mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=yWs65ess;       spf=pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=hirerush@hirerush.com'}, 
						13{'name': 'DKIM-Signature', 'value': 'v=1; a=rsa-sha256; c=relaxed/relaxed;        d=hirerush-com.20150623.gappssmtp.com; s=20150623;        h=from:message-id:date:subject:to:mime-version:x-original-sender         :x-original-authentication-results:precedence:mailing-list:list-id         :list-post:list-help:list-archive:list-subscribe:list-unsubscribe;        bh=mXG1kkxNIjJ5UVoi8yJbhMIDnA0rJ9I/3zkeiOwVRTc=;        b=Gg8OFFERkG8VicwWBAJrgweyMFjARVYQ6NJ8HbkQBVKh7FUxfpJqwb0W1MxnvHFHNN         pNYe8liRTxtlV5SQ+eEyh1X7MlhyE4Em4Q4SenK/lfbB5w+MfDoh04+h3s0pg4S9b7o2         /zyb6+MavzAem3SjhEnenvy4msNcRTqMSitRDf0U4omJLl7kPSGxL6xfE10VgGpugwB0         6dJwSIwqsFnfcbL/poqPWbGssG9ovSWxn36HL+XP04EtaM5uEQcArJaIog5inJvuC637         xvtB5AYmkwPqtOIc8vA6FEgilhh3uw8TAdt8OT97CFzLBckZc8IEKj3PqzF1E6DDV34z         sXwg=='}, 
						14{'name': 'X-Google-DKIM-Signature', 'value': 'v=1; a=rsa-sha256; c=relaxed/relaxed;        d=1e100.net; s=20161025;        h=x-gm-message-state:from:message-id:date:subject:to:mime-version         :x-original-sender:x-original-authentication-results:precedence         :mailing-list:list-id:x-spam-checked-in-group:list-post:list-help         :list-archive:list-subscribe:list-unsubscribe;        bh=mXG1kkxNIjJ5UVoi8yJbhMIDnA0rJ9I/3zkeiOwVRTc=;        b=Q72xeAhc4/OIUa+R/3VyQSPDeBIeDBMIJAzsboNAx1Cp36s0K4Zsoe9G/bjla5m1Ec         h9mrXf2y7hj9Fm53PyllBCLuXisuDfDRBOV2ylGqMtzezViKMFPVxqCaweEFIe1xafKu         Cp0zr/1So6l/oVO+5tXkrLkjCF8fVhaAVxC8utnEvWx3l3AM6erqF/FpZT28UbeEB2kS         iBDVx8+YO7Qn/rFB4FFt70qenU8m2H6Deh1sDck20pgFtpGHyPD1njD/pHJIHpBAII9R         Mgk8TnALZpfpIszzOhb2sks9aHtwGxpnbp8ZP79/swwe4mbGo/c81vHLOyXAGhoforVe         mv4Q=='}, 
						15{'name': 'X-Gm-Message-State', 'value': 'APjAAAXmJYDktDH164aXrYjG3buD03+Lp7xHECfcsO8yyQZQYSk3+mEs Bp7t6ohWypmrj/4PnNtUKR9F1Q=='}, 
						16{'name': 'X-Google-Smtp-Source', 'value': 'APXvYqxqpmCoSAJfbW/LLWQUCV6tGULet/PeHb78l0eOKGQqxxr5rFI5zsLHWYw4GRNR2l80LW95cQ=='}, 
						17{'name': 'X-Received', 'value': 'by 2002:aca:fdc3:: with SMTP id b186mr4553830oii.92.1573750675107;        Thu, 14 Nov 2019 08:57:55 -0800 (PST)'}, 
						18{'name': 'X-BeenThere', 'value': 'support@hirerush.com'}, {'name': 'Received', 'value': 'by 2002:a05:6830:1558:: with SMTP id l24ls1674090otp.3.gmail; Thu, 14 Nov 2019 08:57:54 -0800 (PST)'}, 
						19{'name': 'X-Received', 'value': 'by 2002:a9d:6c8b:: with SMTP id c11mr2151703otr.335.1573750674836;        Thu, 14 Nov 2019 08:57:54 -0800 (PST)'}, 
						20{'name': 'ARC-Seal', 'value': 'i=1; a=rsa-sha256; t=1573750674; cv=none;        d=google.com; s=arc-20160816;        b=QNLinXuGNdiiKCPkXhwv52g9kOblxG3DDmtWhOIqz2roOeW9qMWHV3HOna5l0J/Sv3         USNs3zWsS70AaXLmrhbodGz6NtHaLnvjN1Tv90fK62k7xMvAnPOTKPSDjS8H9jmKTQxL         Vzk22RZIyM3GU7N/we7KF6q4Npl1jBEBT/ynJ+3/YDW1OYGjHUHigB7Jj9r8mpSgorLN         3jC453D44hcNHMLq6qn2c6wukDPYuhZK4gEspHRNft1vO6qFQxWH40ZBf1R/IN764VH5         kpmg1G3BgVWvJgGjW2nY40Fhj1dgYAzNQKlxDWI/yEWFQkzTnpH0T9scm0elH3gf+E4A         Ljog=='}, 
						21{'name': 'ARC-Message-Signature', 'value': 'i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;        h=mime-version:to:subject:date:message-id:from:dkim-signature;        bh=mXG1kkxNIjJ5UVoi8yJbhMIDnA0rJ9I/3zkeiOwVRTc=;        b=mq/Xhi6rGK9R/Fpe7uulmp3Vsc4ODuLEG64WPNthslucoN7MX1KSg1PdkDlNgbGHEt         PaQ32kuM4yHyl+JUuJwY0lrkXFrkjkK9GY7q9TOJsOVsegu4cokbPlcSO2UtoLutc8wX         fdEw+H6TDkyK0Z71RvECQHIaBsemwsbBgqUkZhTOvXbkDqzqA8yWgZNsN80JoXuzbsuY         SywM1z+ZthpEauuuP0ZaXaQKvFeWB9Vz1kZbprAtdwJ+Zgk4c2j7darkPIcqy8DGJ7Z1         q7t12Vy8TdCrLpC5rCVHNGxyTuvnv2EsduTgXK7aW5z5zHgOHXCycxFIaZ4mzywjZEyf         2QDQ=='}, 
						22{'name': 'ARC-Authentication-Results', 'value': 'i=1; mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=yWs65ess;       spf=pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=hirerush@hirerush.com'}, 
						23{'name': 'Received', 'value': 'from mail-sor-f41.google.com (mail-sor-f41.google.com. [209.85.220.41])        by mx.google.com with SMTPS id z9sor3833505oic.37.2019.11.14.08.57.54        for <support@hirerush.com>        (Google Transport Security);        Thu, 14 Nov 2019 08:57:54 -0800 (PST)'}, 
						24{'name': 'Received-SPF', 'value': 'pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) client-ip=209.85.220.41;'}, 
						25{'name': 'X-Received', 'value': 'by 2002:aca:d78a:: with SMTP id o132mr4447327oig.79.1573750674622;        Thu, 14 Nov 2019 08:57:54 -0800 (PST)'}, 
						26{'name': 'Received', 'value': 'from localhost ([209.58.144.244])        by smtp.gmail.com with ESMTPSA id y23sm1855771oih.17.2019.11.14.08.57.53        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);        Thu, 14 Nov 2019 08:57:53 -0800 (PST)'}, 
						27{'name': 'From', 'value': 'hirerush@hirerush.com'}, 
						28{'name': 'Message-ID', 'value': '<4cb03a9305686bb020840557008c0b79@swift.generated>'}, 
						29{'name': 'Date', 'value': 'Thu, 14 Nov 2019 11:57:53 -0500'}, 
						30{'name': 'Subject', 'value': 'Quotes have some problems. Type: General enquiries'}, 
						31{'name': 'To', 'value': 'hirerush@hirerush.com, support@hirerush.com'}, 
						32{'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Type', 'value': 'multipart/alternative; boundary="_=_swift_v4_1573750673_07465395339159ebec2a8d02d0cc93af_=_"'}, 
						33{'name': 'X-Original-Sender', 'value': 'hirerush@hirerush.com'}, 
						34{'name': 'X-Original-Authentication-Results', 'value': 'mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=yWs65ess;       spf=pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=hirerush@hirerush.com'}, 
						35{'name': 'Precedence', 'value': 'list'}, 
						36{'name': 'Mailing-list', 'value': 'list support@hirerush.com; contact support+owners@hirerush.com'}, 
						37{'name': 'List-ID', 'value': '<support.hirerush.com>'}, 
						38{'name': 'X-Spam-Checked-In-Group', 'value': 'support@hirerush.com'}, 
						39{'name': 'X-Google-Group-Id', 'value': '933732647843'}, 
						40{'name': 'List-Post', 'value': '<https://groups.google.com/a/hirerush.com/group/support/post>, <mailto:support@hirerush.com>'}, 
						41{'name': 'List-Help', 'value': '<https://support.google.com/a/hirerush.com/bin/topic.py?topic=25838>, <mailto:support+help@hirerush.com>'}, 
						42{'name': 'List-Archive', 'value': '<https://groups.google.com/a/hirerush.com/group/support/>'}, 
						43{'name': 'List-Subscribe', 'value': '<https://groups.google.com/a/hirerush.com/group/support/subscribe>, <mailto:support+subscribe@hirerush.com>'}, 
						44{'name': 'List-Unsubscribe', 'value': '<mailto:googlegroups-manage+933732647843+unsubscribe@googlegroups.com>, <https://groups.google.com/a/hirerush.com/group/support/subscribe>'}], 
			'body': {'size': 0}, 
			'parts': [{'partId': '0', 
						'mimeType': 'text/plain', 
						'filename': '', 
						'headers': [{'name': 'Content-Type', 'value': 'text/plain; charset=utf-8'}, 
									{'name': 'Content-Transfer-Encoding', 'value': 'quoted-printable'}], 
						'body': {'size': 269, 'data': 'ICAgICAgICBOYW1lOiBRdW90ZXNcbg0KICAgICAgICBFbWFpbDogcG5vZmxpbkBhb2wuY29tXG4NCiAgICAgICAgU3ViamVjdDogR2VuZXJhbCBlbnF1aXJpZXNcbg0KICAgICAgICBNZXNzYWdlOiBJIGdhdmUgYSBxdW90ZSB5ZXN0ZXJkYXkgZm9yIGEgam9iIHRoYXQgSSBkaWQgbm90IGdldC4gSSB3b3VsZCBsaWtlIHRvIGhhdmUgdGhhdCBxdW90ZSBiYWNrIHBsZWFzZS5cbg0KICAgICAgICBDbGllbnQgSVA6IDEwNy43Ny4yMjkuMzYsIDEyNy4wLjAuMVxuDQogICAgDQo='}}, 
						{'partId': '1', 
						'mimeType': 'text/html', 
						'filename': '', 
						'headers': [{'name': 'Content-Type', 'value': 'text/html; charset=utf-8'},
									{'name': 'Content-Transfer-Encoding', 'value': 'quoted-printable'}], 
						'body': {'size': 314, 'data': 'ICAgICAgICA8Yj5OYW1lOjwvYj4gUXVvdGVzPGJyPg0KICAgICAgICA8Yj5FbWFpbDo8L2I-IHBub2ZsaW5AYW9sLmNvbTxicj4NCiAgICAgICAgPGI-U3ViamVjdDo8L2I-IEdlbmVyYWwgZW5xdWlyaWVzPGJyPg0KICAgICAgICA8Yj5NZXNzYWdlOjwvYj4gSSBnYXZlIGEgcXVvdGUgeWVzdGVyZGF5IGZvciBhIGpvYiB0aGF0IEkgZGlkIG5vdCBnZXQuIEkgd291bGQgbGlrZSB0byBoYXZlIHRoYXQgcXVvdGUgYmFjayBwbGVhc2UuPGJyPg0KICAgICAgICA8Yj5DbGllbnQgSVA6PC9iPiAxMDcuNzcuMjI5LjM2LCAxMjcuMC4wLjE8YnI-DQogICAgDQo='}}]},
'sizeEstimate': 11522} 
"""
