import json
import datetime
import threading

from base_plugin import *
import base_plugin

#=============================================Messaging===================================

def send_message(recipient, message, mtype='chat'):
	'''
		Send a message to recipient.

			:param recipient: The To field of your message.
			:param message: the message string to send.
			:para mtype: The message type to send, supports public/private and xmpp style chat/groupchat.
	'''
	if mtype == 'private':
		mtype = 'chat'
	if mtype == 'public':
		mtype = 'groupchat'

	base_plugin.PluginContext.client.send_message(mto=recipient, mbody=message, mtype=mtype)

#=============================================FILTERS=====================================

#FIXME: this seems broken.
def self_message(event, plugin):
	'''
		filter for self generated events.

			:param event: the event being filtered
			:param plugin: the plugin hosting the filter

			returns - true if not self generated event, false otherwise.
	'''
	if msg.From_Nick != plugin.client.nick and plugin.client.nick in msg.Body:
		return True
	return False


def on_message(event, plugin):
	'''
		filter for group chat events.

			:param event: the event being filtered
			:param plugin: the plugin hosting the filter

			returns - true if a group chat event, false otherwise.
	'''
	if event.Type in ["groupchat"]:
		return True
	return False
	

def on_private_message(event, plugin):
	'''
		filter for private message events.

			:param event: the event being filtered
			:param plugin: the plugin hosting the filter

			returns - true if a private message event, false otherwise.
	'''
	if not event.Room:
		return True
	return False


def on_presence(event, plugin):
	'''
		filter for join/part type events.

			:param event: the event being filtered
			:param plugin: the plugin hosting the filter

			returns - true if a presence event, false otherwise.
	'''
	if event.Type in ["available", "unavailable"]:
		return True
	return False

#=============================================FILE OPERATORS=====================================

def put_object_to_file(item, path):
	'''
		Syntactic sugar, write jsonified object to file.

			:param item: Any json-able item.
			:param path: path to log file.
	'''
	with open(path, 'w+') as f:
		f.write(json.dumps(item))


def get_object_from_file(path):
	'''
		Syntactic sugar, read jsonified object from file.

			:param path: path to log file where item is stored.

			Returns - json expanded item from log file.
	'''
	with open(path, 'r') as f:
		item_str = f.read()
		return json.loads(item_str)


def append_to_file(string, path):
	'''
		Syntactic sugar, append string to file.

			:param item: Any json-able item.
			:param path: path to log file.
	'''
	with open(path, 'a') as f:
		f.write(string)


def write_to_file(string, path):
	'''
		Syntactic sugar, write string to file.

			:param item: Any json-able item.
			:param path: path to log file.
	'''
	with open(path, 'w+') as f:
		f.write(string)


def read_from_file(path):
	'''
		Syntactic sugar, read from file.

			:param path: path to log file where item is stored.

			Returns - string contents of log file.
	'''
	with open(path, 'r') as f:
		return f.read()


def read_lines_from_file(path):
	'''
		Read lines from file, as seperated by newline/enter.

			:param path: path to log file

			Returns - list of lines
	'''
	return read_from_file(path).split('\n')

#===========================================TIMED EVENTS=====================================

def schedule_event_by_delay(delay, event, args=[]):
	'''
		Schedule an event by a delay in seconds.

			:param delay: number of seconds until event triggers.
			:param event: the action to be triggered.
			:param args: the arguments to pass when the event is called. (default [])

	'''
	threading.Timer(delay, call_function_with_variable_arguments, [event, args]).start()


def schedule_event(time, event, args=[]):
	'''
		Schedule an event by an absolute time

			:param time: the datetime object representing the trigger time.
			:param event: the action to be triggered.
			:param args: the arguments to pass when the event is called. (default [])

	'''
	delta = time - datetime.datetime.now()
	threading.Timer(delta.total_seconds(), call_function_with_variable_arguments, [event, args]).start()


def schedule_event(year, month, day, hour, minute, second, event, args=[]):
	'''
		Schedule an event by an absolute time

			:param year: year of the event
			:param month: month of the event
			:param day: day of the event
			:param hour: hour of the event
			:param minute: minute of the event
			:param second: second of the event
			:param event: the action to be triggered.
			:param args: the arguments to pass when the event is called. (default [])

	'''
	time = datetime.datetime(year, month, day, hour, minute, second)
	delta = time - datetime.datetime.now()
	threading.Timer(delta.total_seconds(), call_function_with_variable_arguments, [event, args]).start()





#==========================================HERE THERE BE DRAGONS=================================================

def call_function_with_variable_arguments(function, arguments):
	'''
		Takes functions, takes arguments, makes it fit.

			:param function: The function to call
			:param arguments: The argument list to make fit.
	'''
	iterator = len(arguments)

	while True:
		real_exception = None
		try:
			function(*(arguments[:iterator]))
			return

		except Exception as e:
			if not real_exception or "takes exactly" not in str(e) or "arguments" not in str(e):
				real_exception = e

			iterator -= 1
			if iterator < 0:
				raise real_exception


