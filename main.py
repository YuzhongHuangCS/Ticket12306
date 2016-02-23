# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from index import app

container = WSGIContainer(app)
server = HTTPServer(container)
server.listen(8888)
IOLoop.current().start()
