#!/usr/bin/env python3

from utils import arguments
from utils import masscanner as ms
from utils import mkdir
from utils import nmapper as nm
from utils import richard as r
from utils import sqlite as db
from utils import xmlparser
from configparser import ConfigParser
import os
import logging

# Flatfile dirs.
MAIN_DIR = './outputfiles'
ms_dir = os.path.join(MAIN_DIR, 'masscanner')
nm_dir = os.path.join(MAIN_DIR, 'nmapper')
xml_dir = os.path.join(MAIN_DIR, 'xmlfiles')

# Nmapper inputlist Filepath
iL = os.path.join(nm_dir, 'targets.txt')

# Create flatfile dirs
directories = [ms_dir, nm_dir, xml_dir]
dirs = [mkdir.mkdir(directory) for directory in directories]
[logging.info(f'Created directory: {d}') for d in dirs if d is not None]


# DEV
# XmlParser - instance init.
xp = xmlparser.NseParser()
def nse_xmlreader(xmlfile):
	''' 
	arg(s):xmlfile:filepath:str
	'''

	results = []

	# XmlParser - read xml file and parse.
	xp.read_xml(xmlfile)
	# XmlParser - obtain hosts:lst from xml file.
	hosts = xp.get_hosts()
	# XmlParser - obtain ipaddress(es) and nsescript scan result(s) from hosts:lst.
	for host in hosts:
		ipaddress = xp.get_addr(host)
		result = xp.get_hostscript(host)
		# Exclude hossts with no nsescript scan result(s).
		if result is not None:
			i = (ipaddress, result[2], result[0])
			results.append(i)
	
	return results



def main():
	''' Main Func '''

	# Args - init.
	args = arguments.parse_args()

	# Args - configfile
	configfile = args.configfile
		
	# ConfigParser - read onfigfile.
	config = ConfigParser(delimiters='=')
	config.optionxform = str
	config.read(configfile)
	
	if os.path.basename(configfile) == 'masscan.ini':

		# Args - droptable
		if args.drop:
			db.drop_table('Masscanner')

		# ConfigParser - declare dict values.
		MSCONFIG = {k: v for k, v in config['masscanconfig'].items()}
		PORTSCANS = {k: v for k, v in config['portscans'].items()}

		# Sqlite - databse init.
		db.create_table_masscanner()

		# Masscanner - instance init (interface, rate, targets:-iL).
		masscanner = ms.Masscanner(MSCONFIG['interface'], MSCONFIG['rate'], args.inputlist)
		
		# Masscanner - launch scan(s).
		with r.console.status(status=f'[status.text]Scanning') as status:
			for k, v in PORTSCANS.items():
				results = masscanner.run_scan(k, v)
				# Sqlite - insert results (k:ipaddress, v[0]:port, v[1]:protocol, v[2]:description).
				for k, v in results.items():
					db.insert_masscanner(k, v[0], v[1], v[2])
					# Print results.
					print(k, v[0], v[1], v[2])

			# DEV - write database results to file.
			for k, v in PORTSCANS.items():
				filepath = os.path.join(ms_dir, f'{k}.txt')
				results = db.get_ipaddress_by_description(k)
				if results != []:
					with open(filepath, 'w+') as f1:
						[f1.write(f'{result[0]}\n') for result in results]


	elif os.path.basename(configfile) == 'nmap.ini':

		# Args - droptable
		if args.drop:
			db.drop_table('Nmapper')

		# ConfigParser - declare dict values.
		NMCONFIG = {k: v for k, v in config['nmapconfig'].items()}
		NSESCANS = {k: v for k, v in config['nsescans'].items()}

		# Sqlite - databse init.
		db.create_table_nmapper()

		# Nmapper - instance init.
		nmapper = nm.Nmapper()
		
		# Nmapper - launch scan(s).
		with r.console.status(status=f'[status.text]Scanning') as status:
			for k, v in NSESCANS.items():
				# r.console.print(f'[deep_sky_blue3]Scan[/deep_sky_blue3]: {k} = {v}')
				
				# Sqlite - fetch targets by filtering the nse-script scan port.
				results = [i[0] for i in db.get_ipaddress_by_port(v)]
				# targets = ' '.join(results)
				logging.info(f'Found targets in databse.db via port: {v}')

				# DEV - targets.
				with open(iL, 'w+') as f1:
					[f1.write(f'{i}\n') for i in results]
					logging.info(f'Targets written to: {f1.name}')
				
				# Nmapper - launch scan(s).
				oX = os.path.join(xml_dir, f'{k}.xml')
				nmapper.run_scan(k, v, iL, oX)
			
				# XmlParser - read xml file.
				results = nse_xmlreader(oX)
				# Sqlite - insert xml results (i[0]:ipaddress, i[1]:nseoutput, i[2]:nsescript).
				[db.insert_nmapper(i[0], i[1], i[2]) for i in results if i != None]
				# DEV - SMB Signing Print.
				for i in results:
					if i[1] == 'Message signing enabled but not required':
						r.console.print(f'[green][+][/green] {i[0]}: {i[1]}')
					else:
						r.console.print(f'[-] {i[0]}: {i[1]}')

				r.console.print(f'End of scan: {k}\n')
			r.console.print('All scans have completed.\n')

			# DEV - write database results to file.
			for k, v in NSESCANS.items():
				filepath = os.path.join(nm_dir, f'{k}.txt')
				results = db.get_ipaddress_by_nsescript(k)
				if results != []:
					logging.info(f'Found results in databse.db via nsescript: {k}')
					with open(filepath, 'w+') as f1:
						[f1.write(f'{result[0]}, {result[1]}\n') for result in results]
						r.console.print(f'Results written to: {f1.name}')


if __name__ == '__main__':
	main()
