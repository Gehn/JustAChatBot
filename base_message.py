

class Message:
	def __init__(self):
		self.From = None
		self.From_Nick = None
		self.To = None
		self.Room = None
		self.Body = None
		self.Type = None
		self._message = None

	@staticmethod
	def loadXMPP(event):
		'''
			Load a sleekXMPP event as a message.

				:param event: The event to generate a message from.
		'''
		message = Message()
		message._message = event
		message.Body = event["body"]
		message.To = event["to"]
		message.Type = event.get_type()

		if "muc" in event.keys(): #presence
			message.From = event["from"].jid
			message.Room = event["from"].bare
		elif "mucroom" in event.keys() and event["mucroom"]: #Groupchat
			message.From = event["from"].jid
			message.Room = event["mucroom"]
		else: #PM
			message.From = event["from"].jid

		if "mucnick" in event.keys() and event["mucnick"]:
			message.From_Nick = event["mucnick"]

		return message
