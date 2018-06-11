# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup

class UberSlip:

	def __init__(self, messageId, title, body) :
		self.titlemessageId = messageId
		self.body = body
		self.title = title
		self.soup = BeautifulSoup(self.body, 'lxml')
		self.isMain = self.determineMainMessage()
		self.driverName = self.stripDriverName()	
		self.plateNumber = self.stripPlateNumber()
		self.startDatetime = self.stripStartDatetime()
		self.fare = self.stripFare()

		if self.isMain == False :
			# add meta to rental slip html body
			self.body = self.soup.prettify('utf-8')

	def determineMainMessage(self) :
		try :
			priceNode = self.soup.select('.totalPrice.topPrice.tal.black')
			return (len(priceNode) > 0) 
		except Exception, e:
			print ('Error occured determining message type at {}, {}'.format(self.title, e))
			return False

	def stripDriverName(self):
		if self.isMain == False :
			return None
		try :
			driverText = self.soup.select('.driverText')[0].text
			frontRemoved = driverText.replace(u'您本次租車及代僱駕駛 ', '')
			driverName = frontRemoved[:(frontRemoved.index(u' 的行程'))]
			return driverName.encode('utf8')
		except Exception, e :
			print ('Error occured processing driver name at {}, {}'.format(self.title, e))
			return None

	def stripPlateNumber(self) :
		if self.isMain :
			try :
				plateText = self.soup.select('td.fareDisclaimer.tal')[2].text
				return plateText.replace(u'車牌號碼：', '').strip().encode('utf8')
			except Exception, e:
				print ('Error occured processing plate number at {}, {}'.format(self.title, e))
				return None
		else :
			plateText = self.title.replace('Rental Slip - ', '')
			return plateText[:plateText.index(' - ')].strip()
	
	def stripStartDatetime(self) :
		if self.isMain == False :
			return None
		try :
			dateText = self.soup.select('td.rideInfo.gray')[1].text
			startdate = dateText[:dateText.index(u' |')]
			timeText = self.soup.select('span.rideTime.black')[0].text
			startTime = timeText[:timeText.index(u' |')]
			return '{}{}'.format(startdate.encode('utf8'), startTime.encode('utf8')).strip()
		except Exception, e :
			print ('Error occured processing start datetime at {}, {}'.format(self.title, e))
			return None	

	def stripFare(self) :
		if self.isMain == False :
			return None
		try :
			fareText = self.soup.select('.totalPrice.topPrice.tal.black')[0].text
			return fareText.replace(u' $', '').replace(u'.00', '').strip()
		except Exception, e :
			print ('Error occured processing fare at {}, {}'.format(self.title, e))
			return None

	def __str__(self) :
		if self.isMain :
			return 'type:{type} driver:{driver} plate:{plate} time:{starttime} fare:{fare}'.format(type='main',\
																									driver=self.driverName,\
																									plate=self.plateNumber,\
																									starttime=self.startDatetime,\
																									fare=self.fare)
		else :
			return 'type:{} plate:{}'.format('rental', self.plateNumber)



