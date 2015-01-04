import datetime

from base_plugin import *
from plugin_utils import *


class InfoPlugin(Plugin):
	def initialize(self):
		self.add_command("!info", self.info)
		self.add_command("!listcommands", self.listCommands)


	def info(self, message):
		info_str = "\nBuilt with the tri_bot framework\n"
		info_str += "Copyright (c) 2014, Mr.N\n"
		info_str += "BSD License\n"

		self.send_message(message.From, info_str)

	def listCommands(self, message):
		self.send_message(message.From, str(PluginContext.client.list_commands()))

#@Command
#def ListCommands(message):
#	send_message(message.From, PluginContext.client.list_commands())
