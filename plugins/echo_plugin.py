import datetime

from base_plugin import *
from plugin_utils import *


class EchoPlugin(Plugin):
	def initialize(self):
		self.add_command("!echo", self.echo)
		self.add_command("!remindme", self.remind_me)

		self.reminders = {}


	def echo(self, message):
		schedule_event_by_delay(2, self.echo_message, [message])


	def echo_message(self, message):
		info_str = "Echo.\n"
		self.send_message(message.From, info_str)

				
	def remind_me(self, message, delay_string, *reminder):
		self.reminders[message.From] = " ".join(reminder)
		
		delay_string = delay_string.strip().lower()
		delay = -1

		for unit_of_time, number_of_seconds_in_unit in [['s', 1], ['m', 60], ['h', 3600], ['d', 86400]]:
			if unit_of_time in delay:
				delay = (int)(delay_string.split(unit_of_time)[0]) * number_of_seconds_in_unit

		if delay == -1:
			target_datetime = None
			try:
				target_datetime = datetime.datetime.strptime(delay_string, "%m/%d/%Y-%H:%M")
			except ValueError as exception:
				pass
			try:
				target_datetime = datetime.datetime.strptime(delay_string, "%m/%d/%Y")
			except ValueError as exception:
				pass

			if target_datetime:
				delay = (target_datetime - datetime.datetime.now()).total_seconds()

		if delay == -1:
			raise ValueError			

		schedule_event_by_delay(int(delay), self.remind_me_callback, [message.From])


	def remind_me_callback(self, recipient):
		self.send_message(recipient, str(self.reminders[recipient]))
