# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup
from enum import Enum

class UberSlipType(Enum) :
	NewMain = 0
	OldMain = 1
	Rental = 2

class UberSlip:

	def __init__(self, messageId, title, body) :
		self.titlemessageId = messageId
		self.body = body
		self.title = title
		self.soup = BeautifulSoup(self.body, 'lxml')
		self.slipType = self.determineSlipType()
		self.driverName = self.stripDriverName()	
		self.plateNumber = self.stripPlateNumber()
		self.startDatetime = self.stripStartDatetime()
		self.fare = self.stripFare()
		#add to dic key, in case of duplicated plate number (same uber car in same month)
		self.date = self.stripStartDate()

		if self.slipType == UberSlipType.Rental:
			# add meta to rental slip html body
			
			self.soup.html.body.insert_before(self.soup.new_tag('head'))
			metaEle = self.soup.new_tag('meta')
			metaEle['http-equiv'] = 'Content-Type'
			metaEle['content'] = 'text/html; charset=utf-8'
			self.soup.html.head.append(metaEle)
			self.body = self.soup.prettify()

	def determineSlipType(self) :
		'''
		determine message type: newMain(after mid sept 2018)  oldMain rental
		Return: 
			enum UberSlipType
		'''
		try :
			# old main
			priceNode = self.soup.select('.totalPrice.topPrice.tal.black')
			if len(priceNode) > 0 :
				print('Old Main')
				return UberSlipType.OldMain

			priceNode = [ x for x in self.soup.find_all('td',attrs={'align':'right'}) if 'Uber18_p3' in x.get('class')]	
			if len(priceNode) > 0 :
				print('New Main')
				return UberSlipType.NewMain

			print('Rental')
			return UberSlipType.Rental
		except Exception, e:
			errMsg = 'Error occured determining message type at {}, {}'.format(self.title, e)
			raise ValueError(errMsg)

	def stripDriverName(self):
		if self.slipType == UberSlipType.Rental :
			return None
		try :
			if self.slipType == UberSlipType.OldMain :
				driverText = self.soup.select('.driverText')[0].text
				frontRemoved = driverText.replace(u'您本次租車及代僱駕駛 ', '')
				driverName = frontRemoved[:(frontRemoved.index(u' 的行程'))]
				return driverName.encode('utf8')
			elif self.slipType == UberSlipType.NewMain :
				driverText = [ x.string for x in self.soup.find_all('td') if x.string != None and u'您本次租車' in  x.string ][0]
				frontRemoved = driverText.strip().replace(u'您本次租車及代僱駕駛', '')
				driverName = frontRemoved[:(frontRemoved.index(u' 的行程'))]
				return driverName.encode('utf8')
		except Exception, e :
			print ('Error occured processing driver name at {}, {}'.format(self.title, e))
			return None

	def stripPlateNumber(self) :
		if self.slipType == UberSlipType.OldMain :
			try :
				# if user gave uber their tw id number.
				plateText = self.soup.select('td.fareDisclaimer.tal')[1].text
				if plateText.find(u'車牌號碼') < 0 :
					# user did not gave id to uber
					plateText = self.soup.select('td.fareDisclaimer.tal')[2].text
				return plateText.replace(u'車牌號碼：', '').strip().encode('utf8')
			except Exception, e:
				print ('Error occured processing plate number at {}, {}'.format(self.title, e))
				return None
		
		if self.slipType == UberSlipType.NewMain :
			try :
				plateText = [ x.string for x in self.soup.find_all('td') if x.string != None and u'車牌號碼：' in  x.string ][0]
				return plateText.strip().replace(u'車牌號碼： ', '').strip().encode('utf8')
			except Exception, e:
				print ('Error occured processing plate number at {}, {}'.format(self.title, e))
				return None

		plateText = self.title.replace('Rental Slip - ', '')
		return plateText[:plateText.index(' - ')].strip()

	def stripStartDate(self) :
		'''
		strip out date
		Return :
			int of date, eg: 30
		'''
		dateTimeString = self.stripStartDatetime()
		if self.slipType == UberSlipType.Rental :
			#19.07.2018 1:04#
			return int(dateTimeString[:dateTimeString.index('.')]) #return 19
		
		if self.slipType == UberSlipType.OldMain :
			#2018年7月19日109 
			dateTimeString = dateTimeString[dateTimeString.find('\xe6\x9c\x88') + len('\xe6\x9c\x88'):] #月 #月19日109
			return int(dateTimeString[0:dateTimeString.find('\xe6\x97\xa5')]) #日 #return 19
		
		if self.slipType == UberSlipType.NewMain :
			dateText = [ x.string for x in self.soup.find_all('span') if   x.string != None and u'月' in  x.string and x.get('class') != None and 'Uber18_text_p1' in x.get('class')][0]
			#週六, 10月 20, 2018
			startdate = dateText[dateText.index(u'月') + 1:][:dateText.index(',')].strip()
			return int(startdate) #20

	def stripStartDatetime(self) :
		if self.slipType == UberSlipType.Rental :
			# minute of two slips might not match
			plateText = self.title.replace('Rental Slip - ', '')
			rslipDatetime = plateText[plateText.index('- ') + len('- '):].strip() #19.07.2018 1:04
			return rslipDatetime

		if self.slipType == UberSlipType.OldMain :
			try :
				dateText = self.soup.select('td.rideInfo.gray')[1].text
				startdate = dateText[:dateText.index(u' |')]
				startdate = startdate.strip()
				timeText = self.soup.select('span.rideTime.black')[0].text
				startTime = timeText[:timeText.index(u' |')]
				startTime = startTime.replace(':', '').strip()
				return '{}{}'.format(startdate.encode('utf8'), startTime.encode('utf8')).strip()
			except Exception, e :
				print ('Error occured processing start datetime at {}, {}'.format(self.title, e))
				return None	
		
		if self.slipType == UberSlipType.NewMain :
			try :
				dateText = [ x.string for x in self.soup.find_all('span') if   x.string != None and u'月' in  x.string and x.get('class') != None and 'Uber18_text_p1' in x.get('class')][0]
				#週六, 10月 20, 2018
				startdate = dateText[dateText.index(u', ') + 1:].strip()
				#10月 20, 2018
				timeText = [ x.string for x in self.soup.find_all('td') if   x.string != None and u':' in  x.string and x.get('class') != None and 'Uber18_text_p2' in x.get('class')][0]
				startTime = timeText.replace(':', '').strip()
				return '{} {}'.format(startdate.encode('utf8'), startTime.encode('utf8')).strip()
				#10月 20, 2018 2139
			except Exception, e :
				print ('Error occured processing start datetime at {}, {}'.format(self.title, e))
				return None	

	def stripFare(self) :
		if self.slipType == UberSlipType.Rental :
			return None
		try :
			if self.slipType == UberSlipType.OldMain :
				fareText = self.soup.select('.totalPrice.topPrice.tal.black')[0].text
				return fareText.replace(u' $', '').replace(u'.00', '').strip()
			
			if self.slipType == UberSlipType.NewMain :
				priceText = [ x.string for x in self.soup.find_all('td',attrs={'align':'right'}) if 'Uber18_p3' in x.get('class')][0]
				priceString = priceText.replace('$', '')
				priceString = priceString[:priceString.index('.')].strip()
				return priceString

		except Exception, e :
			print ('Error occured processing fare at {}, {}'.format(self.title, e))
			return None

	def __str__(self) :
		if self.slipType == UberSlipType.OldMain :
			return 'type:{type} driver:{driver} plate:{plate} time:{starttime} fare:{fare}'.format(type='main',\
																									driver=self.driverName,\
																									plate=self.plateNumber,\
																									starttime=self.startDatetime,\
																									fare=self.fare)
		else :
			return 'type:{} plate:{}'.format('rental', self.plateNumber)



