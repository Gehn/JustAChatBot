import os

from plugin_utils import *


class Plugin:
	def __init__(self, client):
		self._message_triggers = []
		self._commands = {}

		self.client = client

		self.initialize() #To give me freedom to play with this later without breaking the API.


	def add_command(self, command, function):
		'''
			Add a command for the specified plugin to be triggered on, via private message.
			Additional space seperated tokens in the private message are taken as arguments.

				:param command: command string to trigger on
				:param function: function to run when command is triggered
		'''
		self._commands[command] = function
		print "			Adding command <" + command + "> for function <" + function.__name__ + "> for plugin <" + self.__class__.__name__ + ">"


	def add_trigger(self, new_trigger):
		'''
			Add a filter for this plugin to trigger on.  Filter should return true if the plugin
			should trigger.

				:param new_tigger: function to be called on to filter events the plugin should be called on.
		'''
		self._message_triggers.append(new_trigger)
		print "			Adding trigger <" + new_trigger.__name__ + "> for plugin <" + self.__class__.__name__ + ">"


	def _get_triggers(self):
		return self._message_triggers


	#TODO: decide if I want this here or just in pluginUtils
	def send_message(self, recipient, message, mtype='chat'):
		'''
			Send a message string to recipient.

				:param recipient: The To field of the message; JID in xmpp; of the recipient.
				:param message: The message string to send.
				:param mtype: The type of message to send, private or public. (also supports xmpp style chat vs groupchat)
		'''
		if mtype == 'private':
			mtype = 'chat'
		if mtype == 'public':
			mtype = 'groupchat'

		self.client.send_message(mto=recipient, mbody=message, mtype=mtype)


	def initialize(self):
		'''
			User defined initialization, called at plugin initialization. Override this as needed.
		'''
		pass


	def __call__(self, message):
		'''
			Run the plugin against a message.

				:param message: The message to run against.
		'''
		self._run(message)


	def _run(self, message):
		'''
			Internal meta-run, wraps user defined run.

				:param message: event this run is triggered on.
		'''

		#Run commands.  Currently limited to private messages.
		if on_private_message(message, self):
			message_body_tokens = message.Body.split()

			for command, command_function in self._commands.items():
				if len(message_body_tokens) and message_body_tokens[0].strip() == command.strip():
					try:
						print "RUNNING COMAND:", [message] + message_body_tokens[1:]
						call_function_with_variable_arguments(command_function, [message] + message_body_tokens[1:])

					except Exception as e:
						self.client.send_message(mto=message.From, mbody="COMMAND ERROR", mtype='chat')
						print "COMMAND ERROR:", command, ":", e


		#Make sure we should even run (not be filtered.)
		#No filters means no messages get through.
		filtered = True
		for plugin_trigger in self._message_triggers:
			try:
				if plugin_trigger(message, self):
					filtered = False
			except Exception as e:
				print "PLUGIN TRIGGER ERROR:", plugin_trigger, ":", e
				return
		if filtered:
			return


		#Actually run.
		try:
			self.run(message)
		except Exception as e:
			print "PLUGIN ERROR:", self, ":", e


	def run(self, message):
		'''
			The business end of a plugin.  Runs whenever it is triggered, according to filtering rules.
			Override this for most plugin functionality.

				:param message: The message this plugin triggered on.
		'''
		return



class PluginContext:
	client = None

	commands = []

	triggers = {}


def Command(function):
	'''
		Decorator: turns the top level function into a command

			:param function: The function to decorate. (to turn into a command)
	'''
	print "	Registering command: " + str(function)

	PluginContext.commands.append(function)
	return function


def Trigger(trigger_type):
	'''
		Decorator: turns the top level function into a triggered function.

			:param trigger_type: The function that determines what events this decorated function should trigger on.
	'''
	def TriggerDecorator(function):
		print "	Registering trigger: " + str(trigger_type)
		print "		Registering trigger to function: " + str(function)

		try:
			PluginContext.triggers[function].append(trigger_type)
		except:
			PluginContext.triggers[function] = [trigger_type]


		return function

	return TriggerDecorator


def Schedule(delay):
	'''	Decorator: turns the top level function into a scheduled function.

			:param delay: how long (in seconds) should this function delay before firing.
	'''
	def ScheduleDecorator(function, args=[]):
		print "	Scheduling delay: " + str(trigger_type)
		print "		Scheduling delay for function: " + str(function)

		schedule_event(delay, function, args)

		return function

	return ScheduleDecorator

