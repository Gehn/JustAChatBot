from base_plugin import *
from plugin_utils import *

from datetime import datetime
import time


class LogPlugin(Plugin):
	def initialize(self):
		self.add_trigger(on_message)

		self.add_command("!chatsearch", self.search)
		self.add_command("!chatreplay", self.replay)


	def run(self, message):
		append_to_file(str(datetime.now()) + " : " + message.From + " : " + message.Body + '\n', "chatlog.log")


	def search(self, message, query, *additional_queries):
		chat_history = read_lines_from_file("chatlog.log")
		chat_history.reverse()

		found_line = None
		for line in chat_history:
			if query in line:
				found_line = line
				for additional_query in additional_queries:
					if additional_query not in line:
						found_line = None
						break

				if found_line:
					break

		if found_line:
			self.send_message(message.From, line)

		return

	def replay(self, message, startTime, endTime = None):
		start_time = None
		end_time = None
		try:
			start_time = datetime.strptime(startTime, "%Y-%m-%d,%H:%M")
			if endTime:
				end_time = datetime.strptime(endTime, "%Y-%m-%d,%H:%M")
		except Exception as e:
			self.send_message(message.From, "Expects inputs in the format: !chatreplay <yyyy-mm-dd,hh:mm> [<yyyyy-mm-dd,hh:mm>]  ;  " + str(e))
			return


		chat_history = read_lines_from_file("chatlog.log")

		for line in chat_history:
			line_tokens = line.split(" : ")

			line_time = None
			try:
				line_time = datetime.strptime(line_tokens[0], "%Y-%m-%d %H:%M:%S.%f")
			except:
				continue
			
			#2.6 compatibility.
			delta = (line_time - start_time)
			delta_seconds = (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10**6

			if ((line_time > start_time ) \
					and ( end_time and line_time < end_time )) \
				or (not end_time and abs(delta_seconds) < 10):
					self.send_message(message.From, line)
					time.sleep(1)

		self.send_message(message.From, "Done replay.")
