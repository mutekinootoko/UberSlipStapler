# -*- encoding: utf-8 -*-
# python 2.7

import argparse
from GmailServiceWrap import GmailServiceWrap
import datetime
import pdfkit
import os
from UberSlip import UberSlipType

# FILL THIS
GMAIL_USER_ID = None

def stapleAndPrintSlips(slips, year, month) :
	'''
	Staple matching slips toghter and print to pdf 

	Returns:
		void
	'''
	# dictionary{plate_date:UberSlip}, eg: 30(int):RBS3913
	rentalSlips = {}
	mainSlips = {}
	for us in slips :
		if us.slipType == UberSlipType.OldMain or us.slipType == UberSlipType.NewMain:
			mainSlips['{}_{}'.format(us.plateNumber, us.date)] = us
		else :
			rentalSlips['{}_{}'.format(us.plateNumber, us.date)] = us

	dirname = '{}-{}'.format(year, month)
	try :
		os.makedirs(dirname)
	except OSError, ose :
		pass

	if len(mainSlips) != len(rentalSlips) :
		# missing matching slip
		print ('There are {} main slips, but {} rental slips.'.format(len(mainSlips), len(rentalSlips)))
		if len(mainSlips) > len(rentalSlips) :
			# try find missing slip
			for platenumberAndDate, mainSlip in mainSlips.iteritems() :
				try :
					rslip = rentalSlips[platenumberAndDate] 
				except KeyError, ke:
					print ('MISSING rental slip at {datetime} with plate number {plate} fare {fare}, check with uber app.'.format(datetime=mainSlip.startDatetime,
																										plate=mainSlip.plateNumber,
																										fare=mainSlip.fare))
		else :
			for platenumberAndDate, rslip in rentalSlips.iteritems() :
				try :
					mslip = mainSlips[platenumberAndDate]
				except KeyError, ke:
					print ('MISSING main slip plate {plate}, check with uber app.'.format(plate=rslip.plateNumber))


	for platenumberAndDate, mainSlip in mainSlips.iteritems() :
		#print platenumber
		try :
			rentalSlip = rentalSlips[platenumberAndDate]
		except KeyError, ke:
			continue
		
		filename = './{dir}/{datetime}-{drivername}-{plate}-{fare}'.format(dir=dirname,
																		datetime=mainSlip.startDatetime,
																		drivername=mainSlip.driverName,
																		plate=mainSlip.plateNumber,
																		fare=mainSlip.fare)
		htmlfileMainpath = '{filename}-main.html'.format(filename=filename)
		htmlfileRentalpath = '{filename}-rental.html'.format(filename=filename)
		# write html to file
		with open(htmlfileMainpath, 'w') as h1f :
			try :
				h1f.write(mainSlip.body)
			except UnicodeDecodeError, e:
				print ('UnicodeDecodeError at main slip, {} {} '.format( mainSlip.plateNumber, e))
				pass
		with open(htmlfileRentalpath, 'w') as h2f :
			try :
				h2f.write(rentalSlip.body.encode('utf-8'))
			except UnicodeDecodeError, e:
				print ('UnicodeDecodeError at rental slip, {} {} '.format( rentalSlip.plateNumber, e))
				pass
		# write to pdf 
		pdffilepath = '{filename}.pdf'.format(filename=filename)
		try :
			pdfkit.from_file([htmlfileMainpath, htmlfileRentalpath], pdffilepath)
		except Exception, e:
			pass
		print 'main receipt:{}, rental slip:{}, output pdf: {}'.format(mainSlip, rentalSlip, pdffilepath)



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

	print ('Search for uber slips in {}/{}'.format(year, month))	

	gmailServiceWrap = GmailServiceWrap(GMAIL_USER_ID, args)
	'''
	for us in gmailServiceWrap.getUberSlips(year, month) :
		print '{}'.format(us)
	'''
	#print gmailServiceWrap.uberSlipsSearch(year, month)
	uberSlips = gmailServiceWrap.getUberSlips(year, month)
	print ('there are {} slips.'.format(len(uberSlips)) )
	stapleAndPrintSlips(uberSlips, year, month)





