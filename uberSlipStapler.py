requirements.txt# -*- encoding: utf-8 -*-
# python 2.7

import argparse
from GmailServiceWrap import GmailServiceWrap
import datetime
import pdfkit
import os

# FILL THIS
GMAIL_USER_ID = None

def stapleAndPrintSlips(slips, year, month) :
	'''
	Staple matching slips toghter and print to pdf 

	Returns:
		void
	'''
	# dictionary{plate:UberSlip}
	rentalSlips = {}
	mainSlips = {}
	for us in slips :
		if us.isMain :
			mainSlips[us.plateNumber] = us
		else :
			rentalSlips[us.plateNumber] = us

	dirname = '{}-{}'.format(year, month)
	try :
		os.makedirs(dirname)
	except OSError, ose :
		pass

	for platenumber, mainSlip in mainSlips.iteritems() :
		rentalSlip = rentalSlips[platenumber]
		filename = './{dir}/{datetime}-{drivername}-{plate}-{fare}'.format(dir=dirname,
																		datetime=mainSlip.startDatetime,
																		drivername=mainSlip.driverName,
																		plate=mainSlip.plateNumber,
																		fare=mainSlip.fare)
		htmlfileMainpath = '{filename}-main.html'.format(filename=filename)
		htmlfileRentalpath = '{filename}-rental.html'.format(filename=filename)
		# write html to file
		with open(htmlfileMainpath, 'w') as h1f :
			h1f.write(mainSlip.body)
		with open(htmlfileRentalpath, 'w') as h2f :
			h2f.write(rentalSlip.body)
		# write to pdf 
		pdffilepath = '{filename}.pdf'.format(filename=filename)
		try :
			pdfkit.from_file([htmlfileMainpath, htmlfileRentalpath], pdffilepath)
		except Exception, e:
			pass
		print '{} | {} | {}'.format(mainSlip, rentalSlip, pdffilepath)



if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-m", "--month", type=int, default=0,
					help="month to search in number, Jan=1, default: current month")
	parser.add_argument("-y", "--year", help="year to search, default: current year", type=int, default=0) #0=current year
	args = parser.parse_args()
	month = args.month
	year = args.year
	if month is 0 :
		month = datetime.datetime.now().month
	if year is 0 :
		year = datetime.datetime.now().year

	settingfile = './settings.py'
	if os.path.isfile(settingfile) :
		execfile(settingfile)
		print ('loading from settings file.')

	print ('Search for uber slip in {}/{}'.format(year, month))	

	gmailServiceWrap = GmailServiceWrap(GMAIL_USER_ID, args)
	'''
	for us in gmailServiceWrap.getUberSlips(year, month) :
		print '{}'.format(us)
	'''
	#print gmailServiceWrap.uberSlipsSearch(year, month)
	uberSlips = gmailServiceWrap.getUberSlips(year, month)
	print ('there are {} slips.'.format(len(uberSlips)) )
	stapleAndPrintSlips(uberSlips, year, month)





