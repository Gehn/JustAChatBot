'''
import datetime

	Plugins can import anything they want of python for their use.

from base_plugin import *

	This will get you all of the "standard" framework stuff you need.  Comes with
		Plugin (the class you inherit from to build plugins for)
		as well as all the utilities and filters in PluginUtils.py.

		NOTE: you also get a bunch of other convenience functions, like write_to_file,
		put_object_to_file, etc.  Look around in PluginUtils.py, basically, and at the
		other example plugins for how to use these.
		LastSeenPlugin.py is basically an example of how you can do almost everything
		just as raw python.
		LogPlugin.py is an example of how to use the API for almost everything.
		You can use as much or as little as you like.


class TestPlugin(Plugin):		NOTE: All class plugins must inherit from Plugin.
	def initialize(self):

			Define the initialize method as so if needed to perform
			stateful initialization of the plugin.  This happens before it is ever run.

		print "Initializing test plugin."	
		self.add_trigger(on_message)	

			The add_trigger function is the first utility of note.  provided with
			a filter, (which can be defined custom if needed, see PluginUtils.py)
			it ensures that your plugin will run whenever that type of message occurs.
			You can apply as many filters as you'd like.  Any one succeeding allows the message through.
			NOTE: you can use the filters as functions anywhere else in your plugin as well.

		self.add_command("!test", self.test)

			The add_command utility is another builtin which allows you to make "commands",
			functions triggered by a command string sent via private message to the bot,
			which directly call a specified function.  whitespace seperated items following
			the initial command are interpreted as arguments to the function.


	def run(self, message):

			The primary method of the plugin, called whenever the plugin triggers as defined
			by the filters added in initialization.  The message argument is the message
			which triggered this run of the plugin.  See below for the commonly used parts of the message.

		print "Running test plugin on: "
		print message					Some common fields:
		print "to:", message.To				-to: the target of the message (you, the bot.)
		print "room:", message.Room			-room: the group chat room, if this message is a group chat message.
		print "from:", message.From			-from: the entity sending the message. This has useful subcomponents.
		print "type:", message.Type			-type: the type of the message. (chat, groupchat, available, unavailable, etc.)
		print "body:", message.Body 			-body: the body of the message.
		print "________________________"


	def test(self, message, *args):

			An example of a command-triggered function.  The Message argument is the message which
			triggered the command.  For demonstration, this function also can take a variable number
			of additional args which it will print to the command line, before in any case replying
			"Success." to the sender.

		for arg in args:			if the *args stuff is confusing you, look up python varargs; 
			print "got:", arg		it's just for show of the private message tokens to function argument translation here.

		self.send_message(message.From, "Success")

			This is how you reply to a message.  Pretty straightforward.


@Command
def AnotherTest(message):

		Some functionality can also be defined outside of classes, for small standalones.

		This would be called via '!AnotherTest'

	send_message(message.From, "Echo")





NOTE:
To see further examples, look at the other files in the ./plugins directory.  To see full functionality, help(BasePlugin) and help(PluginUtils) may be of some assistance.

'''
