import datetime

from base_plugin import *
from plugin_utils import *


class LastSeenPlugin(Plugin):
	def initialize(self):
		self.last_seen_map = {}
		self.last_spoke_map = {}
		self.last_said_map = {}

		self.add_trigger(on_message)
		self.add_trigger(on_presence)
		self.add_trigger(on_private_message)

		try:
			self.last_seen_map = get_object_from_file("lastseen.log")
			self.last_spoke_map = get_object_from_file("lastspoke.log")
			self.last_said_map = get_object_from_file("lastsaid.log")
		except:
			pass


	def run(self, message):
		if on_presence(message, self):
			if message.Type == "available":
				self.last_seen_map[message.From] = "online now"

			if message.Type == "unavailable":
				self.last_seen_map[message.From] = str(datetime.datetime.now())

			put_object_to_file(self.last_seen_map, "lastseen.log")


		if on_message(message, self):
			self.last_spoke_map[message.From] = str(datetime.datetime.now())
			put_object_to_file(self.last_spoke_map, "lastspoke.log")

			self.last_said_map[message.From] = str(datetime.datetime.now()) + " : " + message.Body
			put_object_to_file(self.last_said_map, "lastsaid.log")


		if on_private_message(message, self):
			message_body_tokens = message.Body.split()

			reply_body = ""

			if len(message_body_tokens) == 2 and message_body_tokens[0] == "!lastseen":

				if message_body_tokens[1] in self.last_seen_map:
					reply_body = '\n' + str(message_body_tokens[1]) + " last seen: " + str(self.last_seen_map[message_body_tokens[1]])
				else:
					for (user, time) in self.last_seen_map.items():
						if message_body_tokens[1].lower() in user.lower():
							reply_body += '\n' + str(user) + " last seen: " + str(time)
							
						
				if message_body_tokens[1] in self.last_spoke_map:
					reply_body = '\n' + str(message_body_tokens[1]) + " last spoke: " + str(self.last_spoke_map[message_body_tokens[1]])
				else:
					for (user, time) in self.last_spoke_map.items():
						if message_body_tokens[1].lower() in user.lower():
							reply_body += '\n' + str(user) + " last spoke: " + str(time)

			elif len(message_body_tokens) >= 2 and message_body_tokens[0] == "!lastsaid":
				print "GOT LASTSAID"

				if message_body_tokens[1] in self.last_seen_map:
					reply_body = '\n' + str(message_body_tokens[1]) + " last said: " + str(self.last_seen_map[message_body_tokens[1]])
				else:
					for (user, time) in self.last_said_map.items():
						if message_body_tokens[1].lower() in user.lower():
							reply_body += '\n' + str(user) + " last said: " + str(time)
			
			if reply_body:
				print "sending: ", reply_body
				self.send_message(message.From, reply_body)
