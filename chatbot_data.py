import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from time import sleep
import time
import base64
import email
import json
from datetime import datetime
import sqlite3
import re


def fill_base(frame):
# Automatic filling the data base with scraped information

	connection = sqlite3.connect('./for_hirerush.db')
	cursor = connection.cursor()
	try:
		cursor.execute('CREATE TABLE chatbot_data (date_time TEXT, sender TEXT, receiver TEXT, history_id TEXT, id TEXT, snippet TEXT, response_id TEXT, message TEXT)')
	except Exception as e:
		pass
	cursor.execute("INSERT INTO chatbot_data VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
		(str(frame['date_time']), frame['sender'], str(frame['receiver']), str(frame['history_id']), str(frame['id']), str(frame['snippet']), str(frame['response_id']), str(frame['message'])))
	connection.commit()
	cursor.close()
	connection.close()






#client_id = '487116948591-cqa8brsmmmunotlkkujvnugifmtuj9c4.apps.googleusercontent.com'
#client_key = 'xiIVK6LySCZTNsDj9FmOGOsR'
#frame = pd.DataFrame(columns=['date_time', 'sender', 'history_id', 'id', 'snippet', 'response_id', 'message', 'receiver'])
#frame.set_index('id')
frame = pd.Series()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

service = build('gmail', 'v1', credentials=creds)


request = service.users().messages().list(userId='me')
# time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(1236472051807/1000.0))



def get_all_the_mail():

	frame = pd.Series()

	SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

	flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
	creds = flow.run_local_server(port=0)

	service = build('gmail', 'v1', credentials=creds)


	request = service.users().messages().list(userId='me')
	while request is not None:
		try:

			response = request.execute()
			for each in response['messages']:
				msg = service.users().messages().get(userId='me', id=each['id'], format='raw').execute()
				# dict_keys(['id', 'threadId', 'labelIds', 'snippet', 'historyId', 'internalDate', 'sizeEstimate', 'raw'])
				msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
				try:
					raw_msg = msg_str.decode('ASCII')
					if ('hirerush@hirerush.com' in raw_msg.split('From:')[1].split('<')[1].split('>')[0] and 'Client IP:' not in msg['snippet']) \
					or 'payments@hirerush.com' in raw_msg.split('From:')[1].split('<')[1].split('>')[0] \
					or 'support.hirerush.com' in raw_msg.split('From:')[1].split('<')[1].split('>')[0] or '@app.bamboohr.com' in raw_msg.split('From:')[1].split('<')[1].split('>')[0] \
					or ('@swift.generated' in raw_msg.split('From:')[1].split('<')[1].split('>')[0] and 'Client IP:' not in msg['snippet']):
						continue
					else:
						if 'Calls Tasks Date To Clients To Providers' in msg['snippet']:
							continue
						else:
							#print(base64.urlsafe_b64decode(msg['raw'].encode('ASCII')))
							#sleep(5)
							frame['date_time'] = datetime.fromtimestamp(int(msg['internalDate'])/1000)
							frame['sender'] = raw_msg.split('From:')[1].split('<')[1].split('>')[0]
							try:
								frame['receiver'] = raw_msg.split('Delivered-To:')[1].split('\n')[0].strip()
							except Exception:
								frame['receiver'] = raw_msg.split('From:')[1].split('To:')[1].split('\n')[0].strip()
							frame['history_id'] = msg['historyId']
							frame['id'] = msg['id']
							frame['snippet'] = msg['snippet'][:50]
							frame['response_id'] = ' '
							try:
								frame['message'] = raw_msg.strip('\n').strip('\r').split('Content-Transfer-Encoding:')[1]
							except Exception:
								frame['message'] = raw_msg.strip('\n').strip('\r')
							print(frame['message'])
							#print(raw_msg.strip('\n').strip('\r').split('Content-Transfer-Encoding:')[1])
				except Exception as e:
					print(e)
				print(frame)
				fill_base(frame)
				#print('--------------------------------------------------')
				#sleep(1)
				#print(msg.strip())

			request = service.users().messages().list_next(previous_request=request,previous_response=response)
			print('end of the loop')
			sleep(5)

		except Exception:
			sleep(300)
			pass


def get_all_the_mail_test():

	email_pattern = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'

	SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

	flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
	creds = flow.run_local_server(port=0)

	service = build('gmail', 'v1', credentials=creds)


	request = service.users().messages().list(userId='me')

	while request is not None:
		response = request.execute()
		for each in response['messages']:
			msg = service.users().messages().get(userId='me', id=each['id'], format='full').execute()
			# dict_keys(['id', 'threadId', 'labelIds', 'snippet', 'historyId', 'internalDate', 'sizeEstimate', 'raw'])
			#msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
			#try:
			print(msg['payload']['headers'][0]['value'])
			try:
				email_re = re.search(email_pattern, msg['payload']['headers'][27]['value'])
				email = email_re.group(0).strip('<').strip('>')
			except Exception:
				email = msg['payload']['headers'][27]['value']

			print(email)

			print(msg['payload']['headers'][29]['value'])

			print(msg['payload']['headers'][30]['value'])

			print(msg['payload']['headers'][31]['value'])
			try:
				print(msg['payload']['parts'][0])
			except Exception:
				continue

			message = base64.urlsafe_b64decode(msg['payload']['parts'][0]['body']['data'].encode())
			print(message.decode())


		request = service.users().messages().list_next(previous_request=request,previous_response=response)
		print('end of the loop')
		sleep(5)


get_all_the_mail_test()


"""
{'partId': '', 
'mimeType': 'multipart/alternative', 
'filename': '', 
'headers': [0{'name': 'Delivered-To', 'value': 'val@hirerush.com'}, 
			1{'name': 'Received', 'value': 'by 2002:a0c:87a9:0:0:0:0:0 with SMTP id 38csp2023433qvj;        Tue, 12 Nov 2019 07:16:53 -0800 (PST)'}, 
			2{'name': 'X-Received', 'value': 'by 2002:aca:3208:: with SMTP id y8mr4269137oiy.112.1573571813798;        Tue, 12 Nov 2019 07:16:53 -0800 (PST)'}, 
			3{'name': 'ARC-Seal', 'value': 'i=3; a=rsa-sha256; t=1573571813; cv=pass;        d=google.com; s=arc-20160816;        b=kBolkkTGxGuSY+PnMOYZAiUAoppRfJE1VBI7bylXUUn5APuMf2PDZCpH6It6ozu8Oc         Jl4w7QYE/XkUfvrOTvtYXqd3sbGAdGJx83C0TsjohfmcGde5rGSLiE+PE2TKWZ/YFYjA         TCZtk1f5k1yW0MGojeys75MIwrFSG5E51Mx3khOOQDPYPsT/4+eQ2Z7uqrQSTnLHa0ZD         OVi+cUPKHLnNHDe/kvXN+FdA1bHqXkCBgfu6a56emvg5X/JDhXpjy0seX2g8o20qDezJ         tsJr6FcG0P/KNZ+1aLqVETqKrRFtmaQIupOBVm1wLfFlqXu1l919/DtklcUfoX160s7x         ivfw=='}, 
			4{'name': 'ARC-Message-Signature', 'value': 'i=3; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;        h=list-unsubscribe:list-subscribe:list-archive:list-help:list-post         :list-id:mailing-list:precedence:mime-version:to:subject:date         :message-id:from:dkim-signature;        bh=9DNmhr8lGzvRAg+tYNEbo5rXVMOHx6kxyD58ntfchIk=;        b=khY41CWRHQptD9j7XM/QM8h62ykSVWhaqiCY3QnIiQ6uV5mjGamWsNcF2RCIKCzN55         LibBS2CwHnFZoBea9k7NUQ3Vg71mL2QxFox+SB+qNQ3M2B7c/paLGyntERHAK8Jc9Xrl         qV6jgAUKkqy/Mc2WXT1uaI6iQw7uQnPLKK1xU+bTU+fvHjU4REgjGejneOWLBI6nFqKA         6+1a0oop7qvew91fhwRlRAk6cNrXIrdxGyAWnpqMxH9cedgr7uQ+vQx4IpP+nzHumhL3         /5ZgUmao6q0pDGac3DRPNeg3SFeG9BBGzjXzm43cd71IVTRIoT6MVuxPo2GRv2/aGny+         DEtg=='}, 
			5{'name': 'ARC-Authentication-Results', 'value': 'i=3; mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=czdDoOoJ;       arc=pass (i=2 spf=pass spfdomain=hirerush.com dkim=pass dkdomain=hirerush-com.20150623.gappssmtp.com);       spf=pass (google.com: domain of support+bncbdz3r57izyprbzmzvpxakgqe3j7sl2i@hirerush.com designates 209.85.220.69 as permitted sender) smtp.mailfrom=support+bncBDZ3R57IZYPRBZMZVPXAKGQE3J7SL2I@hirerush.com'}, 
			6{'name': 'Return-Path', 'value': '<support+bncBDZ3R57IZYPRBZMZVPXAKGQE3J7SL2I@hirerush.com>'}, 
			7{'name': 'Received', 'value': 'from mail-sor-f69.google.com (mail-sor-f69.google.com. [209.85.220.69])        by mx.google.com with SMTPS id t191sor14405167oif.69.2019.11.12.07.16.53        for <val@hirerush.com>        (Google Transport Security);        Tue, 12 Nov 2019 07:16:53 -0800 (PST)'}, 
			8{'name': 'Received-SPF', 'value': 'pass (google.com: domain of support+bncbdz3r57izyprbzmzvpxakgqe3j7sl2i@hirerush.com designates 209.85.220.69 as permitted sender) client-ip=209.85.220.69;'}, 
			9{'name': 'Authentication-Results', 'value': 'mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=czdDoOoJ;       arc=pass (i=2 spf=pass spfdomain=hirerush.com dkim=pass dkdomain=hirerush-com.20150623.gappssmtp.com);       spf=pass (google.com: domain of support+bncbdz3r57izyprbzmzvpxakgqe3j7sl2i@hirerush.com designates 209.85.220.69 as permitted sender) smtp.mailfrom=support+bncBDZ3R57IZYPRBZMZVPXAKGQE3J7SL2I@hirerush.com'}, 
			10{'name': 'ARC-Seal', 'value': 'i=2; a=rsa-sha256; t=1573571813; cv=pass;        d=google.com; s=arc-20160816;        b=s4jMXVf1b8KvpFOY1lp2EcEKAZmec3NZGRoCjLC35bIF87WyvBrIyBx54XlusXK1NU         nOxYpN/Dj+hzjZf1b9EC4aOnnrs1K6npOwTGeUUNuLDlnbSuHBVCnfPqHkHzpziTE6Ik         OPzy+HUDb22gTJvzRwrnRqh5UOAW1PvsVZgONZSHDMpej6c3oaq2+E+tGzJ/f8h7se5B         wXVzi+0gKyDIK8opiw36DjVk+FSUjxc128kl6oFnIl3gmLchiR3WtVNf+k8IqnngyDxy         ZD0vHtsSYryxwj5Kwz1EP5n0UaUOW03RMWBmYFqC2txYdUZdc8qRVac6FefuwJaWueh8         dRAw=='}, 
			11{'name': 'ARC-Message-Signature', 'value': 'i=2; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;        h=list-unsubscribe:list-subscribe:list-archive:list-help:list-post         :list-id:mailing-list:precedence:mime-version:to:subject:date         :message-id:from:dkim-signature;        bh=9DNmhr8lGzvRAg+tYNEbo5rXVMOHx6kxyD58ntfchIk=;        b=OWEHSUm4fk74QmxZ64W8ZZxPgurmdLCmK7Kdh2R4rwPkXeGw4Bo/AQM4NvKt29GW7s         MfOJ58BtUhvsF08I1JcycJSVb5VlOtyCtNr8BKhWZaAk3ACUr+FarEEpHLcDPxfQ0j1l         wL3a0WcZegOYSzWTO5NyjBdciPXwQl/W4LDupQeoIHlcX+cNaZ81pH9ubRnVu0sn78sG         OGDwjxpaCJU7qkt/N+hjcfhmvN3mth3WAlm3ziPMnxEX4SO69HanmB38Ehi3nJUz5PsN         KH9DdSiZiRCoUY2s0DmnATDP2oL1qcUvOs2ylEStOJhgN0X0FqM9cbD+NNeBdH4vLOki         lWuA=='}, 
			12{'name': 'ARC-Authentication-Results', 'value': 'i=2; mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=XVtpJLLc;       spf=pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=hirerush@hirerush.com'}, 
			13{'name': 'DKIM-Signature', 'value': 'v=1; a=rsa-sha256; c=relaxed/relaxed;        d=hirerush-com.20150623.gappssmtp.com; s=20150623;        h=from:message-id:date:subject:to:mime-version:x-original-sender         :x-original-authentication-results:precedence:mailing-list:list-id         :list-post:list-help:list-archive:list-subscribe:list-unsubscribe;        bh=9DNmhr8lGzvRAg+tYNEbo5rXVMOHx6kxyD58ntfchIk=;        b=czdDoOoJO09tkMd/jlB5ZI14kd6JxrpUzsAly+Sa6GvQwNn60HO2KEzw3W0E7XBwBh         w/1TepnKuX4UojcCuDyzB4Idp+ASLsj0QWSXDcnpWZIV7sNQuuPIpSu1AV0YY6dQCTLw         MttUnXp+X2qG+S8IdQkKAm3cTRayF4EVho0RKRdfZQ7EWE8bqNOXOefvaeEDZhkFl5Mt         /hWCaN0UrteZAXw2U55VNXZUMrGLB+/IGFeFr54B6nFmoyfG1gUpp3g4dxYkGBYgzAXc         q2HsPypYv7tcUD/lbKGbJOir1XhBYfTavc9GeuvjevV7ZsgeIjuhxkZOV2PFZMxwlUiA         Fezw=='}, 
			14{'name': 'X-Google-DKIM-Signature', 'value': 'v=1; a=rsa-sha256; c=relaxed/relaxed;        d=1e100.net; s=20161025;        h=x-gm-message-state:from:message-id:date:subject:to:mime-version         :x-original-sender:x-original-authentication-results:precedence         :mailing-list:list-id:x-spam-checked-in-group:list-post:list-help         :list-archive:list-subscribe:list-unsubscribe;        bh=9DNmhr8lGzvRAg+tYNEbo5rXVMOHx6kxyD58ntfchIk=;        b=KQ2ZzzRHDBlQwiGhkmJ5NzLJkWiZ9qJTy/ZLGPAg0WZSjeosSjh2DsODeR7XiG4iyQ         OtUT//oCQt/Hqd1arhUXytwuqkKH/XJaCEMCFxh0T1QI62fU1o2E9zVN9smuCQfJceFO         Nsel8xfwdtB9sG3Ap/oFXF2USJSN2rmIVfX5BgfVyiSsqNG/mNchZaIovizq0LnpViGb         6AJHii4IkTwYyZXF9KUQjajS7hsqjPK3je/MRrYhFw1a77okgi2wl0p9yMZD0o7rgVbL         rbLlsptwjrb9dIapJ3QLugkWr0G2WMF/oAWEPPvI2U9Nqg45K63gGaRi2eQ1CC6i1MHb         rLJQ=='}, 
			15{'name': 'X-Gm-Message-State', 'value': 'APjAAAWwGhvqlcqEpMMp5iDj+/vXhVRHgZoMULyIr6DMTR98WXEXFNJ7 DaVFLZXEmGn2kSmePiFH32FAOw=='}, 
			16{'name': 'X-Google-Smtp-Source', 'value': 'APXvYqwzdIzMS/u7ZS9zbjbGAZe9K/ZQH3kPaUvhtem8wPfghh4UbqwSM8tXyvM8cRLeGvyPmGAfLA=='}, 
			17{'name': 'X-Received', 'value': 'by 2002:a05:6808:8e9:: with SMTP id d9mr4264567oic.29.1573571813433;        Tue, 12 Nov 2019 07:16:53 -0800 (PST)'}, 
			18{'name': 'X-BeenThere', 'value': 'support@hirerush.com'}, {'name': 'Received', 'value': 'by 2002:a9d:7085:: with SMTP id l5ls2964237otj.11.gmail; Tue, 12 Nov 2019 07:16:53 -0800 (PST)'}, 
			19{'name': 'X-Received', 'value': 'by 2002:a9d:1b70:: with SMTP id l103mr25995553otl.154.1573571813127;        Tue, 12 Nov 2019 07:16:53 -0800 (PST)'}, 
			20{'name': 'ARC-Seal', 'value': 'i=1; a=rsa-sha256; t=1573571813; cv=none;        d=google.com; s=arc-20160816;        b=eVgZTcQIg19CiErtQKErrMQeRrY0ohPLGSP9+GASbGKNkdWhwP3TGFQWmdbP4mOjMD         LVYWd49Su/GNwlyeD8zBxFaEssmTZ1XK/EGgDgpJY6UVJlOxhKzteVLYlbo3LwcDGB5q         9CWiwg/HGtKSMjEJoTCuVbnQ5Ol5ckH6IpaZT7L1wT3bD6Q8Q882Vxm6YWFASUNaod+W         z4aQY0q5GWuWdThWc5XmtACxVO5nallepF8CpNAt+2k8iZju4Yx/9b2Z6EhjwG9mUxt2         4eRgWaZOFw1NUz/78dsAxq0kLNc5ygojvb5MqfX43FSgILHm+3KtSm3SoiAtu9QknXrn         zlTQ=='}, 
			21{'name': 'ARC-Message-Signature', 'value': 'i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;        h=mime-version:to:subject:date:message-id:from:dkim-signature;        bh=9DNmhr8lGzvRAg+tYNEbo5rXVMOHx6kxyD58ntfchIk=;        b=Yiomi758Kes1BaeP7R/PClTT0bxHxZNaartl/xz1MJ+lRLF8oJYAUtgB7adR2hPSh5         qhVSoZRRyTrnlfoV1iDNpOI77US2ExKvCeLJvPBASRGA4iFlJmVk0q+OP4/0g6lrq1j+         r5hV5AoRr1S2rFtw2+1twHMHQmZiVz6UOwYzBRRYLn1wGHqL3Gr96B4qdyqXJXUM0kxw         HPpeyHLdkFREeSPQOSRu45o8Db9xqVP2AO3aeoUAbAdMsU+PRRrFRuDGIo3lacI6Lnzh         PQnkGGegPhDOrYBXeky+xLE56BnAV1o8p0wxaoDXgxROIWcEcWE4eWAeBuQGmL+HDUnj         sNjw=='}, 
			22{'name': 'ARC-Authentication-Results', 'value': 'i=1; mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=XVtpJLLc;       spf=pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=hirerush@hirerush.com'}, 
			23{'name': 'Received', 'value': 'from mail-sor-f41.google.com (mail-sor-f41.google.com. [209.85.220.41])        by mx.google.com with SMTPS id e63sor13831920otb.75.2019.11.12.07.16.53        for <support@hirerush.com>        (Google Transport Security);        Tue, 12 Nov 2019 07:16:53 -0800 (PST)'}, 
			24{'name': 'Received-SPF', 'value': 'pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) client-ip=209.85.220.41;'}, 
			25{'name': 'X-Received', 'value': 'by 2002:a9d:bb6:: with SMTP id 51mr26939510oth.158.1573571812395;        Tue, 12 Nov 2019 07:16:52 -0800 (PST)'}, 
			26{'name': 'Received', 'value': 'from localhost ([209.58.144.244])        by smtp.gmail.com with ESMTPSA id 47sm6391350otu.37.2019.11.12.07.16.49        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);        Tue, 12 Nov 2019 07:16:49 -0800 (PST)'}, 
			27{'name': 'From', 'value': '"HireRush.com" <hirerush@hirerush.com>'}, 
			28{'name': 'Message-ID', 'value': '<d381ccb09af1d948d8f15470f4797d75@swift.generated>'}, 
			29{'name': 'Date', 'value': 'Tue, 12 Nov 2019 10:16:49 -0500'}, 
			30{'name': 'Subject', 'value': 'Unverified smartform (phone check phase)'}, 
			31{'name': 'To', 'value': 'support@hirerush.com, hirerush@hirerush.com'}, 
			32{'name': 'MIME-Version', 'value': '1.0'}, 
			33{'name': 'Content-Type', 'value': 'multipart/alternative; boundary="_=_swift_v4_1573571809_319ddb631b648608fc531b1d5c15ca81_=_"'}, 
			34{'name': 'X-Original-Sender', 'value': 'hirerush@hirerush.com'}, {'name': 'X-Original-Authentication-Results', 'value': 'mx.google.com;       dkim=pass header.i=@hirerush-com.20150623.gappssmtp.com header.s=20150623 header.b=XVtpJLLc;       spf=pass (google.com: domain of hirerush@hirerush.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=hirerush@hirerush.com'}, 
			{'name': 'Precedence', 'value': 'list'}, 
			{'name': 'Mailing-list', 'value': 'list support@hirerush.com; contact support+owners@hirerush.com'}, 
			{'name': 'List-ID', 'value': '<support.hirerush.com>'}, 
			{'name': 'X-Spam-Checked-In-Group', 'value': 'support@hirerush.com'}, 
			{'name': 'X-Google-Group-Id', 'value': '933732647843'}, 
			{'name': 'List-Post', 'value': '<https://groups.google.com/a/hirerush.com/group/support/post>, <mailto:support@hirerush.com>'}, 
			{'name': 'List-Help', 'value': '<https://support.google.com/a/hirerush.com/bin/topic.py?topic=25838>, <mailto:support+help@hirerush.com>'}, 
			{'name': 'List-Archive', 'value': '<https://groups.google.com/a/hirerush.com/group/support/>'}, 
			{'name': 'List-Subscribe', 'value': '<https://groups.google.com/a/hirerush.com/group/support/subscribe>, <mailto:support+subscribe@hirerush.com>'}, 
			{'name': 'List-Unsubscribe', 'value': '<mailto:googlegroups-manage+933732647843+unsubscribe@googlegroups.com>, <https://groups.google.com/a/hirerush.com/group/support/subscribe>'}], 
'body': {'size': 0}, 
'parts': [{'partId': '0', 'mimeType': 'text/plain', 'filename': '', 'headers': [{'name': 'Content-Type', 'value': 'text/plain; charset=utf-8'}, 
																				{'name': 'Content-Transfer-Encoding', 'value': 'quoted-printable'}], 
		'body': {'size': 39, 'data': 'CVBsZWFzZSwgbG9vayBhdCBIVE1MIGVtYWlsIHZlcnNpb24NCg0K'}}, 
		{'partId': '1', 'mimeType': 'text/html', 'filename': '', 'headers': [{'name': 'Content-Type', 'value': 'text/html; charset=utf-8'}, 
																			{'name': 'Content-Transfer-Encoding', 'value': 'quoted-printable'}], 
'body': {'size': 1205, 'data': 'CTxoMj5Vc2VyIHJpZ2h0IG5vdyBmaW5pc2ggdHlwaW5nIGhpcyBwaG9uZS4gUGhvbmUgaXM6ICsxMjE2MjEwMjM2NjwvaDI-DQoJPHA-VXNlciBzYXlzLCB0aGF0IGhlL3NoZSBsb2NhdGVkIGluIHppcDogPHN0cm9uZz40NDEyMjwvc3Ryb25nPjwvcD4NCgk8cD4gSGVyZSBhcmUgYW5zd2VycyB0byBzbWFydGZvcm0gcXVlc3Rpb25zIChPaCwgc21hcnRmb3JtIHdhczogPHN0cm9uZz5Mb2NhbCBNb3ZpbmcgKHVuZGVyIDUwIG1pbGVzKTwvc3Ryb25nPik8L3A-DQoJPHA-DQoJCTx1bD4NCgkJCQkJCQkJCQkJPGxpPjxzdHJvbmc-TmVlZCBNb3Zpbmc6PC9zdHJvbmc-IDIgYmVkcm9vbSBob21lPC9saT4NCgkJCQkJCQkJCQkJCQkJCTxsaT48c3Ryb25nPlR5cGUgb2YgcHJvcGVydHk6PC9zdHJvbmc-IEFwYXJ0bWVudDwvbGk-DQoJCQkJCQkJCQkJCQkJCQk8bGk-PHN0cm9uZz5SZWxvY2F0aW9uIGRpc3RhbmNlOjwvc3Ryb25nPiBMZXNzIHRoYW4gNSBtaWxlczwvbGk-DQoJCQkJCQkJCQkJCQkJCQk8bGk-PHN0cm9uZz5BZGRpdGlvbmFsIHNlcnZpY2VzOjwvc3Ryb25nPiBGdXJuaXR1cmUgYXNzZW1ibHkgYW5kIGRpc2Fzc2VtYmx5PC9saT4NCgkJCQkJCQkJCQkJCQkJCTxsaT48c3Ryb25nPk51bWJlciBvZiBib3hlczo8L3N0cm9uZz4gMSAtIDEwIGJveGVzPC9saT4NCgkJCQkJCQkJCQkJCQkJCTxsaT48c3Ryb25nPlN0YWlycyBhdCBwcmltYXJ5IGxvY2F0aW9uOjwvc3Ryb25nPiBZZXMsIHRoZSBtb3ZlciB3aWxsIG1vdmUgaXRlbXMgdXAvZG93biBzdGFpcnM8L2xpPg0KCQkJCQkJCQkJCQkJCQkJPGxpPjxzdHJvbmc-U3RhaXJzIGF0IGRlc3RpbmF0aW9uIGxvY2F0aW9uOjwvc3Ryb25nPiBZZXMsIHRoZSBtb3ZlciB3aWxsIG1vdmUgaXRlbXMgdXAvZG93biBzdGFpcnM8L2xpPg0KCQkJCQkJCQkJCQkJCQkJPGxpPjxzdHJvbmc-U2NoZWR1bGUgb2YgcmVsb2NhdGlvbjo8L3N0cm9uZz4gQXMgc29vbiBhcyBwb3NzaWJsZTwvbGk-DQoJCQkJCQkJCQkJCQkJCQk8bGk-PHN0cm9uZz5BZGRpdGlvbmFsIGluZm86PC9zdHJvbmc-IE5vdCBzcGVjaWZpZWQ8L2xpPg0KCQkJCQkJCQkJPC91bD4NCgk8L3A-DQoNCgk8cD5Vc2VyIGhhcyBub3QgZmluaXNoZWQgc3VibWlzc2lvbiB5ZXQuIFBsZWFzZSBhbGxvdyBmb3IgMy01IG1pbnV0ZXMgYmVmb3JlIGF0dGVtcHRpbmcgdG8gdGFrZSBvdmVyIGFuZCB2ZXJpZnkuPC9wPg0KDQo='}}]}

"""