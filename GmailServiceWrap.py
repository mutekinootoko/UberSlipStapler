# -*- encoding: utf-8 -*-

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from calendar import monthrange
from UberSlip import UberSlip
import base64
import email



class GmailServiceWrap:
	
	def __init__(self, gmailUserId, args):
		'''
		Arguments:
			gmailUserId:
			args: args = parser.parse_args(), from argparse
		'''
		self.gmailService = self.createGmailService(args)
		self.gmailUserId = gmailUserId

	def createGmailService(self, args) :
		'''
		access gmail service
		'''
		args.noauth_local_webserver = True
		args.logging_level='DEBUG'
		#args.logging_level='WARNING'
		# Setup the Gmail API
		SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
		store = file.Storage('credentials.json')
		creds = store.get()
		if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
			creds = tools.run_flow(flow, store, args)
			print ('store credentials to local.')
		service = build('gmail', 'v1', http=creds.authorize(Http()))

		return service

	def uberSlipsSearch(self, year, month) :
		'''
		apply search string to gmail service

		Returns:
			array of message id strings.
		'''
		lastDayOfMonth = monthrange(year, month)[1]
		searchQuery = 'from:(uber.com) 出租單 after:{year}/{monthInt}/01 before:{year}/{monthInt}/{lastDay}'.format(year=year, monthInt=month, lastDay=lastDayOfMonth)
		print ('search query {}'.format(searchQuery))

		response = self.gmailService.users().messages().list(userId=self.gmailUserId, q=searchQuery).execute()
		messageIds = []
		if 'messages' in response:
			for m in response['messages'] :
				messageIds += [m['id']]

		while 'nextPageToken' in response:
			page_token = response['nextPageToken']
			response = self.gmailService.users().messages().list(userId=self.gmailUserId, q=searchQuery, pageToken=page_token).execute()
			for m in response['messages'] :
				messageIds += [m['id']]

		return messageIds

	def extractUberSlipMessageTitleBodyByMessageId(self, messageId) :
		'''
		search single gmail by message id

		Returns:
			tuple(title, body)
		'''
		response = self.gmailService.users().messages().get(userId=self.gmailUserId, id=messageId, format="full").execute()
		if 'parts' in response['payload'] :
			# has payload.parts
			#response['payload']['parts'] has two elements, one body, one for attachment
			bodies = [ f['body']['data']  for f in response['payload']['parts'] if f['mimeType'] == 'text/html']
			body = bodies[0]
		else :
			# no payload.parts
			body = response['payload']['body']['data']
		messageBody = base64.urlsafe_b64decode(body.encode('ASCII'))
		#print messageBody
		title =[ f['value']  for f in response['payload']['headers'] if f['name'] == 'Subject' ][0]
		return (title, messageBody)
		'''
		message = self.gmailService.users().messages().get(userId=self.gmailUserId, id=messageId, format="raw").execute()
		msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
		return email.message_from_string(msg_str)
		'''

	def getUberSlips(self, year, month) :
		'''
		Returns:
			array of UberSlip
		'''
		uberSlips = []
		try :
			uberMessageIds = self.uberSlipsSearch(year, month)
		except Exception, e:
			print ('Unable to search slips.')
			return []

		for messageId in uberMessageIds :
			try :
				messageTitleBody = self.extractUberSlipMessageTitleBodyByMessageId(messageId)
				uberSlips += [UberSlip(messageId, messageTitleBody[0], messageTitleBody[1])]
			except Exception, ee :
				print ('Error occured when processing message:{} . {}'.format(messageId, ee))
				continue
		return uberSlips 



