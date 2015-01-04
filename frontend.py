#!/usr/bin/env python
 
import curses
import curses.textpad
import time

from plugin_utils import *

class TerminalFrontend:
	'''
		Text based curses terminal frontend for the bot.
	'''
	def __init__(self, stdscr=None):
		'''
			Initialize the frontend.

				:param stdscr: The curses main window, if one exists.
		'''
		self.message_queues = {}
		self.channel = ""

		if not stdscr:
			self.main_window = curses.initscr()
		else:
			self.main_window = stdscr

		self.on_enter_triggers = []
		self.on_enter_triggers.append(self.send_to_channel)

		self._should_exit = False

		self.input_buffer = ""

		self.init_window()


	def init_window(self):
		'''
			Initialize the geometry of the display window, given the current size.
		'''
		(self.max_y, self.max_x) = self.main_window.getmaxyx()

		self.output_start_x = 5
		self.output_start_y = 5

		self.output_max_x = self.max_x - 30
		self.output_max_y = self.max_y - 10

		self.channels_start_x = self.output_max_x + 4
		self.channels_start_y = self.output_start_y		

		self.channels_max_x = self.max_x - 4 
		self.channels_max_y = self.output_max_y

		self.line_length = self.output_max_x - self.output_start_x

		self.input_buffer_start_y = self.max_y - 5
		self.input_buffer_start_x = self.output_start_x

		self.input_buffer_max_y = self.max_y - 1
		self.input_buffer_max_x = self.output_max_x


	def send_to_channel(self, message):
		'''
			Send a string to the active channel.

				:param message: The message to send.
		'''
		self.message_queues[self.channel].reverse()
		self.message_queues[self.channel].append("Sending:" + message + " to " + self.channel)
		try:
			if '/' in self.channel:
				send_message(self.channel, message, 'chat') 
			else:
				send_message(self.channel, message, 'groupchat')
		except Exception as e:
			self.message_queues[self.channel].append(str(e))
		self.message_queues[self.channel].reverse()


	def add_trigger_on_enter(self, function):
		'''
			Add a function to be called when the enter key is hit.

				:param function: The callback to be triggered.
		'''
		self.on_enter_triggers.append(function)


	def display_message(self, message):
		'''
			Takes a new message object and handles it appropriately, displaying it in its queue.

				:param message: The message to display.
		'''
		if message.Room:
			new_channel = message.Room
		else:
			new_channel = message.From

		if new_channel not in self.message_queues:
			self.message_queues[new_channel] = []

		if not self.channel:
			self.channel = new_channel

		aligned_message_block = ['\n', message.From] # 'mucnick' and 'mucroom' ('muc' in status messages)
		if message.From_Nick:
			aligned_message_block = ['\n', message.From_Nick]

		for i in xrange(0, len(message.Body), self.line_length):
			aligned_message_block.append(message.Body[i:i+self.line_length])


		self.message_queues[new_channel].reverse()

		for line in aligned_message_block:
			self.message_queues[new_channel].append(line)

		self.message_queues[new_channel].reverse()

		self.message_queues[new_channel] = self.message_queues[new_channel][:self.output_max_y]

		self.paint()


	def paint(self):
		'''
			Paint the screen.  Should be called per "tick"
		'''
		self.main_window.clear()

		lines = self.message_queues[self.channel]
		print_position = self.output_max_y
		for line in lines:
			try:
				self.main_window.addstr(print_position, self.output_start_x, line)
			except:
				pass
			print_position -= 1

			if print_position < self.output_start_y:
				break

		print_position = self.channels_start_y
		for channel in self.message_queues.keys():
			if channel == self.channel:
				channel = '=' + channel + '='

			channel = channel[:(self.channels_max_x - self.channels_start_x)]

			try:
				self.main_window.addstr(print_position, self.channels_start_x, channel)
			except:
				pass
			print_position += 1

			if print_position > self.channels_max_y:
				break

		self.main_window.addstr(self.input_buffer_start_y, self.input_buffer_start_x,  "> " + self.input_buffer[(-self.line_length - 2):])

		self.main_window.refresh()


	def handle_user_input(self):
		'''
			Handle any key events that have been generated.
		'''
		try:
			c = self.main_window.getkey()
			if c == u"\u001B":			# Escape
				curses.endwin()
				self._should_exit = True
				return

			elif c == u"\u007F" or c == "KEY_BACKSPACE":	# Delete
				self.input_buffer = self.input_buffer[:-1]

			elif c == '\n':				# Enter
				for function in self.on_enter_triggers:
					function(self.input_buffer)

				self.input_buffer = ""

			elif c == "KEY_PPAGE" or c == "KEY_NPAGE":
				if not len(self.message_queues.keys()):
					return

				prev_channel = self.message_queues.keys()[len(self.message_queues.keys())-1]
				next_channel = self.channel
				for channel in self.message_queues.keys():
					if prev_channel == self.channel and c == "KEY_NPAGE":
						next_channel = channel
						break

					if channel == self.channel and c == "KEY_PPAGE":
						break

					prev_channel = channel
						
				if c == "KEY_PPAGE":
					self.switch_channel(prev_channel)

				elif c == "KEY_NPAGE":
					self.switch_channel(next_channel)

			elif c == "KEY_RESIZE":
				self.init_window()
			else:
				self.input_buffer += c

			self.paint()

		#One of my dirtier hacks, for debugging purposes.
		except Exception as e:
			self.input_buffer += str(e)
			self.paint()


	def should_exit(self):
		'''
			Has the user requested that the bot exit?
		'''
		return self._should_exit


	def switch_channel(self, channel):
		'''
			Switch the active channel

				:param channel: The channel to switch to.
		'''
		if channel in self.message_queues:
			self.channel = channel
