# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

import sae
import ssl
import urllib2
import json
import traceback
from sae.mail import send_mail
from datetime import datetime
from tornado.wsgi import WSGIApplication
from tornado.web import RequestHandler

class IndexHandler(RequestHandler):
	def initialize(self):
		self.url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2015-09-13&leftTicketDTO.from_station=PXG&leftTicketDTO.to_station=HZH&purpose_codes=ADULT'
		self.sslcontext = ssl._create_unverified_context()
		self.traincode = (u'K4576', u'T82', u'T79')
		self.emptynum = (u'--', u'无')
		self.recipient = ['1104405025@qq.com', '1041178976@qq.com']
		self.subject = 'Train Ticket Available'
		self.smtp = ('smtp.sina.com', 25, 'scicompass@sina.com', 'scicompass', False)

	def get(self):
		try:
			body = urllib2.urlopen(self.url, context=self.sslcontext).read()

			if body:
				available = {}

				for train in json.loads(body)['data']:
					code = train['queryLeftNewDTO']['station_train_code']
					num = train['queryLeftNewDTO']['yw_num']
					if code in self.traincode and num not in self.emptynum:
						available[code] = num

				self.write(available)

				if available:
					available['timestamp'] = datetime.now().isoformat()
					send_mail(to=self.recipient, subject=self.subject, body=json.dumps(available), smtp=self.smtp)

			else:
				self.set_status(403)
				self.write('Too Many Requests: Empty response body')

		except urllib2.HTTPError as e:
			self.set_status(e.code)
			self.write(e.read())

		except Exception as e:
			self.set_status(500)
			self.write(traceback.format_exc())

app = WSGIApplication(
	handlers = [
		(r'/', IndexHandler),
	],
)

application = sae.create_wsgi_app(app)
