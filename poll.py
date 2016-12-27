# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

import aiohttp
import asyncio
import smtplib  
import traceback
from string import Template
from datetime import datetime

dates = ('2017-01-25', '2017-01-24', '2017-01-23', '2017-01-22', '2017-01-21', '2017-01-20')
traincode = ('T326', 'K2276', 'K1238')
urltemplate = Template('https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=${date}&leftTicketDTO.from_station=HZH&leftTicketDTO.to_station=ZZF&purpose_codes=ADULT')
emptynum = ('--', '无')

host = ''
user = ''
password = ''
recipient = ['']
subject = 'Train Ticket Available'

async def worker(session, date):
	url_date = urltemplate.substitute({'date': date})
	subject_date = "%s on %s" % (subject, date)
	while True:
		try:
			async with session.get(url_date, timeout=10) as res:
				res.raise_for_status()
				avail = {}
				timestamp = datetime.now().isoformat()
				body = await res.json()
				for train in body['data']:
					code = train['queryLeftNewDTO']['station_train_code']
					num = train['queryLeftNewDTO']['yw_num']
					if code in traincode and num not in emptynum:
					avail[code] = num
				if avail:
					avail['timestamp'] = timestamp 
					message = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (user, ", ".join(recipient), subject_date, avail)
					server = smtplib.SMTP_SSL(host)
					server.login(user, password)
					server.sendmail(user, recipient, message.encode('utf-8'))
					server.quit()
					print("[%s]: %s" % (timestamp, subject_date))
					await asyncio.sleep(60)
				else:
					print("[%s]: No %s" % (timestamp, subject_date))
					await asyncio.sleep(5)
		except Exception as e:
			traceback.print_exc()
			await asyncio.sleep(5)

async def master(loop):
	conn = aiohttp.TCPConnector(verify_ssl=False)
	async with aiohttp.ClientSession(connector=conn) as session:
	await asyncio.wait([loop.create_task(worker(session, date)) for date in dates])

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(master(loop))
