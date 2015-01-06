#!/usr/bin/env python

import logging
import os
import inspect
import sys
from threading import Timer
from argparse import ArgumentParser

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import XMPPError
from sleekxmpp.xmlstream.scheduler import Task, Scheduler

from base_plugin import Plugin, PluginContext
from plugin_utils import *
from base_message import Message
from utilities import Log

#If we don't have what we need, just run without the CLI
try:
	from frontend import *
	from curses import wrapper
	FORCENOCLI = False
except Exception as e:
	print "Unable to import CLI dependencies: ", e
	print "Falling back to stdout"
	FORCENOCLI = True


#TODO: rip out init, channel movement, messaging, and termination into hooks and turn "xmpp" into a module.  (also filters.)
class Bot(ClientXMPP):
	'''
		The primary XMPP bot class.
	'''
	def __init__(self, jid, password):
		'''
			Initialize the bot.

				:param jid: The account to log in with.
				:param password: The password to log in with.
		'''
		ClientXMPP.__init__(self, jid, password)

		PluginContext.client = self

		# This is the plugin for multi-user chat.
		self.register_plugin('xep_0045')

		self.add_event_handler("session_start", self.session_start)

		self.add_event_handler("message", self.on_event)
		self.add_event_handler("presence", self.on_event)

		self.nick = None
		self.service = None
		self.channels = []
		self.custom_plugins = []

		self.plugin_dir = "./plugins"

		self.import_plugins()


	def set_nick(self, nick):
		'''
			Set the nick or display name of the bot.
				:param nick: the nickname to use.
		'''
		self.nick = nick


	def set_service (self, service):
		'''
			Set the service URI the bot will utilize for channels.

				:param service: the URI to use.
		'''
		self.service = service


	def set_channels(self, channels):
		'''
			Set the list of channels the bot will join on startup.

				:param channels: the list of channels to join.
		'''
		self.channels = channels


	def add_channel(self, channel):
		'''
			Add a channel to the list of channels the bot will join on startup.

				:param channel: the channel to add.
		'''
		self.channels.append(channel)


	def join_channels(self):
		'''
			Join a list of channels. Must be called after startup.
		'''
		for channel in self.channels:
			self.join_channel(channel)


	def join_channel(self, channel):
		'''
			Join a single channel.  Must be called after startup.

				:param channel: the channel to join.
		'''
		for channel in self.channels:
			if self.service:
				channel = channel + "@" + self.service

			self.plugin['xep_0045'].joinMUC(channel,
				self.nick,
				wait=True)


	def set_plugin_dir(self, plugin_dir):
		'''
			Set where the bot will look for plugins.

				:param plugin_dir: the path to the plugin directory.  All plugins
					should be python files below this path.
		'''
		self.plugin_dir = plugin_dir


	def add_plugin(self, plugin):
		'''
			Add a Plugin class for the bot to utilize.
			The bot will create a unique instance of the Plugin class to run.

				:param plugin: the plugin class to add.
		'''
		self.custom_plugins.append(plugin(self))


	def import_plugins(self):
		'''
			Discover and import all visible plugins from the ./plugins folder in the running directory.
			Must be valid python files, implementing classes which inherit from Plugin, or utilizing
			The standalone decorators @Command and @Trigger.
		'''
		self.custom_plugins = []
		plugin_filenames = []
		for (dirpath, dirnames, filenames) in os.walk(self.plugin_dir):
			plugin_filenames = filenames
			break

		plugin_root = None

		#Accumulate each of the plugin files defined in ./plugins.
		for filename in plugin_filenames:
			base, extension = os.path.splitext(filename)
			if "__init__" not in base and ".py" == extension:
				try:
					plugin_root = __import__("plugins." + os.path.splitext(filename)[0])
					print "Plugin file:", filename
				except Exception as e:
					print "PLUGIN IMPORT ERROR:", e, " FROM FILE:", filename


		print "Plugin module root:", dir(plugin_root)

		#Extract the plugin classes from the plugins module tree.  There's got to be a better way to do this, but I'm bad at things.
		for module, module_name in [(getattr(plugin_root, module_name), module_name) for module_name in dir(plugin_root)]: #For components of the toplevel plugins module (we're looking for plugin files)
			try:
 				# This is a dirty hack but it makes the logs much cleaner.  Not really necessary, we can just fail out without it.
				if module.__class__ == os.__class__:
					print "	From Module:", module
					for plugin, plugin_name in [(getattr(module, plugin_name), plugin_name) for plugin_name in dir(module)]: #For items internal to the modules derived from plugin files.
						try:
							#Total cludge to supress failed import errors on stuff that should fail while allowing errors on user stuff.
							if inspect.isclass(plugin) \
								and plugin != Plugin \
								and issubclass(plugin, Plugin): #Make sure we aren't grabbing the parent class or a builtin.
	
								print "		Plugin:", plugin
								self.add_plugin(plugin)
						except Exception as e:
							print "PLUGIN ADD ERROR:", plugin, ":", e
			except:
				continue

		print "Imported plugins: " + str(self.custom_plugins)	
		return self.custom_plugins


	def session_start(self, event):
		'''
			The callback to be called when the bot first connects (after Process() is called)

				:param event: the start event that triggers this function.
		'''
		logging.debug("Session start")
		self.send_presence()

		try:
			self.get_roster()
		except XMPPError as err:
			logging.error("error:" + str(err))
			self.disconnect()

		self.join_channels()


	def on_event(self, event):
		'''
			The callback to trigger any time an event is captured.

				:param event: The event that triggered this function.
		'''
		event = Message.loadXMPP(event)
		self.run_plugins(event)


	def run_plugins(self, event):
		'''
			Run all plugins on the given event, if appropriate.

				:param event: The event to run against.
		'''
		#print "Got event:" + event + event["body"]
		#Run plugins implemented as children of Plugin
		for plugin in self.custom_plugins:
			try:
				plugin(event)
			except Exception as e:
				print "PLUGIN RUNTIME ERROR:", plugin, ":", e

		#Below is the functionality for running the plugins implemented by standalone decorators. (@Command and @Trigger)
		#Run commands.  Currently limited to private messages.
		if on_private_message(event, self):
			message_body_tokens = event.Body.split()

			for command, command_function in [(function.__name__, function) for function in PluginContext.commands]:
				if len(message_body_tokens) and message_body_tokens[0].strip() == '!' + command.strip():
					try:
						print [event] + message_body_tokens[1:]
						call_function_with_variable_arguments(command_function, [event] + message_body_tokens[1:])
	
					except Exception as e:
						print "COMMAND ERROR:", command, ":", e
						event.reply("COMMAND ERROR:" + str(e)).send()
	

		#Run triggered functions.
		for function, triggers in PluginContext.triggers.items():
			for trigger in triggers:
				try:
					if trigger(event, self):
						call_function_with_variable_arguments(function, [event] + event.Body.split()[1:])
						break
				except Exception as e:
					print "TRIGGER ERROR:", trigger, ":", e


	def list_commands(self):
		'''
			List all the commands currently visible to the bot.
		'''
		commands = [(function.__name__, function) for function in PluginContext.commands]
		for plugin in self.custom_plugins:
			try:
				commands += plugin._commands
			except:
				pass #In case someone wants to cram a function in as a plugin or something.

		return commands



def mainloop(bot, stdscr=None):
	'''
		The main runloop of the program.  If being run in a curses session, stdscr should be populated.

			:param bot: The bot instance that has been prepared.
			:param stdscr: The curses main screen.
	'''
	#If we're running in a curses window... (for the CLI)
	if stdscr:
		console = TerminalFrontend(stdscr)
		bot.custom_plugins.append(console.display_message)
	else: #Otherwise, set up a basic message printer.
		def print_message(event):
			print event.From
			print event.Body

		bot.custom_plugins.append(print_message)

	bot.process(block=False)

	should_halt = False
	while not should_halt:
		if stdscr:
			console.handle_user_input()
			should_halt = console.should_exit()
		else:
			# Exit on escape.  Must hit enter, though.
			if raw_input() == '\x1b':
				should_halt = True
			
		pass

	try:
		bot.abort()
	except:
		exit()	


def main():
	'''
		The main entry point for the bot.
		Mostly parsing args, and the config file, prepares for the mainloop.
	'''
	logging.basicConfig(level=logging.INFO,
				format="%(levelname)-8s %(message)s")

	parser = ArgumentParser()
	parser.add_argument("-c", "--config", dest="config", default="./bot_config.conf")
	parser.add_argument("-u", "--username", dest="username", default=None)
	parser.add_argument("-p", "--password", dest="password", default=None)
	parser.add_argument("--channels", nargs='+', dest="channels", default=[])
	parser.add_argument("--server", dest="server", default=None)
	parser.add_argument("--service", dest="service", default=None)
	parser.add_argument("--nocli", action="store_true", default=False, dest="nocli")
	parser.add_argument("--plugins", dest="plugins", default=None)

	args = parser.parse_args()	

	username = None
	password = None
	server = None
	service = None
	channels = []
	plugin_dir = None

	#Parse the config file.  Should I use a tool for doing this? Probably, but this took all of 10 seconds.
	#Grab config file options first so command line can override them.
	if args.config:
		try:
			with open(args.config) as config_file:
				for line in config_file.readlines():
					line = line.strip()
					if line and line[0] != "#":
						line_tokens = line.split("=")
						if len(line_tokens) >= 2:
							if line_tokens[0].strip().lower() == "username":
								username = line_tokens[1].strip()
							if line_tokens[0].strip().lower() == "password":
								password = line_tokens[1].strip()
							if line_tokens[0].strip().lower() == "server":
								server = line_tokens[1].strip()
							if line_tokens[0].strip().lower() == "service":
								service = line_tokens[1].strip()
							if line_tokens[0].strip().lower() == "channel":
								channels.append(line_tokens[1].strip())
							if line_tokens[0].strip().lower() == "plugins":
								plugin_dir = line_tokens[1].strip()
							
		except:
			pass

	
	

	if args.username:
		username = args.username
	if args.password:
		password = args.password
	if args.server:
		server = args.server
	if args.service:
		service = args.service
	if args.channels != []:
		channels = args.channels
	if args.plugins:
		plugin_dir = args.plugins

	#FIXME: make these reqired via argparser somehow?
	if not username:
		print "Error: no username was supplied."
		sys.exit(-1)
	if not password:
		print "Error: no password was supplied."
		sys.exit(-1)
	if not server:
		print "Error: no server was supplied."
		sys.exit(-1)
	if not service:
		print "Error: no service was supplied."
		sys.exit(-1)

	print "username: ", username
	print "password: ", password[0], '+', len(password)-1
	print "server: ", server
	print "service: ", service
	print "channels: ", channels

	try:
		bot = Bot(username + "@" + server, password)
		bot.set_service(service)
		bot.set_nick(username)
		bot.set_plugin_dir(plugin_dir)
		bot.connect()
		print "Connecting to channels:"
		for channel in channels:
			print "Connecting to channel: ", channel
			bot.add_channel(channel)

		if args.nocli or FORCENOCLI:
			mainloop(bot)
		else:
			def mainloop_wrapper(stdscr):
				mainloop(bot, stdscr)

			wrapper(mainloop_wrapper)

	except Exception as e:
		print e
		exit()


if __name__ == "__main__":
	main()
