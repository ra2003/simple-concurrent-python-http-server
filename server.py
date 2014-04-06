import time
import os
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

HOST_NAME = 'localhost'
PORT_NUMBER = 8080
file_dir = os.getcwd() + '/serverfiles/'
log = []
logLock = threading.RLock()
flights_schedule = {}
flights_schedule_lock = threading.RLock()

# convert the file into filght dict
class Flight():
	def __init__(self, flightID):
		self.flightID = flightID
		self.schedule_info = {}

	def add_scedule_info(self, date, time, ticket):
		self.info = [time, ticket]
		self.schedule_info[date] = self.info

	def add_reservation(self, date):
		if self.schedule_info[date][1] >= 1:
			self.schedule_info[date][1] -= 1
			return 'Reserve Success'
		else:
			return 'Not Enough Tickets'

def get_flights(filename):
	file_in = open(file_dir + filename)
	flights = {}
	for line in file_in:
		line = line.strip('\n\r')
		line_list = line.split(',')
		if not line_list[0] in flights:
			flights[line_list[0]] = Flight(line_list[0])
			flights[line_list[0]].add_scedule_info(line_list[1], line_list[2], 30)
		else:
			flights[line_list[0]].add_scedule_info(line_list[1], line_list[2], 30)
	return flights

# concurrent server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

# sequential server
# class ThreadedHTTPServer(HTTPServer):
# 	pass

class eachLog:
	ipaddress = ''
	dateandtime = ''
	requiredfile = ''
        
class MyHandler(BaseHTTPRequestHandler):
	def do_HEADS(self):
		self.send_response(200)
		self.send_header("Content-type", "text-html")
		self.end_headers()

	def do_GET(self):
		# file_dir = 'C:/Dropbox/Courses/Concurrent Programming/project/webserver/files/'
		# f = open(file_dir + self.path)
		self.send_response(200)
		self.send_header("Content-type", "text-html")
		self.end_headers()
		# self.wfile.write("Entered GET request handler --- ")
		# self.wfile.write(f.read())
		query = self.path.split('-')
		# self.wfile.write(flights_schedule[query[0]].schedule[query[1]])
		if query[0] == 'Query':
			flights_schedule_lock.acquire()
			try:
				flight_info = flights_schedule[query[1]].schedule_info[query[2]]
				res = ' '
				self.wfile.write(flight_info)
			finally:
				flights_schedule_lock.release()

		if query[0] == 'Order':
			flights_schedule_lock.acquire()
			try:
				res = flights_schedule[query[1]].add_reservation(query[2])
				# flight_info = flights_schedule[query[1]].schedule_info[query[2]]
				self.wfile.write(res)
			finally:
				flights_schedule_lock.release()
		# self.wfile.write("Sending response!")
		# create log
		mylog = eachLog()
		mylog.ipaddress = self.client_address[0]
		mylog.dateandtime = self.log_date_time_string()
		mylog.requiredfile = self.path
		# append log
		logLock.acquire()
		log.append(mylog)
		logLock.release()
                

# test(HandlerClass=<class BaseHTTPServer.BaseHTTPRequestHandler>, ServerClass=<class BaseHTTPServer.HTTPServer>)
# Test the HTTP request handler class. This runs an HTTP server on port 8000
# def test(HandlerClass = SlowHandler, ServerClass = ThreadedHTTPServer):
#       _test(HandlerClass, ServerClass)

if __name__ == '__main__':
	# test()
	# get flight dict
	flights_schedule = get_flights('flights.csv')
	server_class = ThreadedHTTPServer
	# if want to test the sequential http server
	# server_class = HTTPServer
	my_server = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
	try:
		my_server.serve_forever()
	except KeyboardInterrupt:
		print '\n'
		for i in log:
		#print i.ipaddress
			print 'log:'+'  '+i.ipaddress+'  '+i.dateandtime+'  '+i.requiredfile
			#print 'log:'+'  '+i.ipaddress+'  '+i.requiredfile+'\t\n'
	my_server.server_close()
	# print flights_schedule['UA001']['Mon']
