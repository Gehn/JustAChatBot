
class _LoggingContext:
	'''
		This class contains the metadata for the logging tooling.

		Attempts to set up a log file.
	'''
	logfile = None
	logging = True

	try:
		logfile = open("./log.log", 'w+')
	except Exception as e:
		print(e)
		print("Logging To File Disabled; falling back to stdout.")


def Log(message, *args):
	'''
		Log a string.  Attempts to log to file (./log.log by default) and
		if it is impossible, writes to stdout.

		:param message: the message string to log.
	'''
	if not IsLoggingOn():
		return

	if args:
		for arg in args:
			message += str(arg)

	if _LoggingContext.logfile:
		_LoggingContext.logfile.write(str(message) + '\n')
	else:
		print(message)


def LoggingOff():
	'''
		Disable logging.
	'''
	Log("Disabling logging.")
	_LoggingContext.logging = False


def LoggingOn():
	'''
		Enable logging.
	'''
	Log("Enabling logging.")
	_LoggingContext.logging = True


def IsLoggingOn():
	'''
		Is logging activated?
	'''
	return _LoggingContext.logging
