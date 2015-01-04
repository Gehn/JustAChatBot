JustAChatBot
============

Simple XMPP bot framework, intending to make scripting as braindead easy as possible.
Comes prerolled for connecting to Star Citizen's chat (in its current form, best attempts will be made to keep it compatible).

Uses a curses frontend (optional) and a sleekXMPP library to speak xmpp.

This is not an exceedingly production ready infrastructure, work needs to be done do modularize the protocol specific bits, fix some naming, and write tests;
There is also a handful of feature/refactor TODOs left before I'll really be happy with it.
No guarantees can be made for XMPP setups that aren't talking to the RSI servers (since that's the only scenario I test in.)


Version:
========
0.1


Running:
========
Run with the following command in the local directory:
 python -m bot

For help:
 python -m bot -h

	NOTE: to quit in --nocli mode, press escape and enter.  To quit in CLI mode, simply hit escape.

Configuration:
==============
Configure the bot using the bot_config.conf file in the local directory.

Add any plugins desired into the local plugins/ directory.
 NOTE: all plugins are just python classes inheriting from Plugin in base_plugin.py, or top level functions with decorators.  See plugins/test_plugin.py for simple examples.



