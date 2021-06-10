#!/usr/bin/env python3

from utils import arguments
from utils import metasploiter
from utils import masscanner
from utils import mkdir
from utils import nmapper
from utils import richard as r
from utils import sqlite as db
from utils import xmlparser
from configparser import ConfigParser
import os
import re
import logging


# Stable versions.
ms_stableversion = '1.3.2'
nm_stableversion = '7.91'

# DEV - rename vars.
# Outputfile dirs.
MAIN_DIR = './outputfiles'
ms_dir = os.path.join(MAIN_DIR, 'portscans')
nm_dir = os.path.join(MAIN_DIR, 'findings')
xml_dir = os.path.join(MAIN_DIR, 'xml')

# Nmap / Metasploit temp target/inputlist filepath.
tmp_targetfile = os.path.join(MAIN_DIR, 'targets.txt')

# Banner
r.banner('Scanman'.upper())

# Create output dirs.
directories = [ms_dir, nm_dir, xml_dir]
dirs = [mkdir.mkdir(directory) for directory in directories]
[logging.info(f'Created directory: {d}') for d in dirs if d is not None]


def func(string):
	# importing the module
	import re
	# declaring the regex pattern for IP addresses
	pattern = re.compile('''((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)
	{3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)''')
	# initializing the list objects
	valid =[]
	invalid=[] 
	# extracting the IP addresses
	for line in string:
		line = line.rstrip()
		result = pattern.search(line)
		# valid IP addresses
		if result:
			valid.append(line)
			return valid
			# # invalid IP addresses 
			# else:
			#   invalid.append(line)
			#   return invalid


def main():
	''' Main Func '''

	# Args - init.
	args = arguments.parse_args()
	# Args - configfile.
	configfile = args.configfile
	# Args - inputlist
	ms_targetfile = args.inputlist
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
		interface = MSCONFIG['interface']
		rate = MSCONFIG['rate']
		# Sqlite - databse init.
		db.create_table_masscanner()

		# Header
		r.console.print(f'[italic grey37]Masscanner\n')
		
		# Masscanner - instance int and run scan.
		for key, value in PORTSCANS.items():
			ms = masscanner.Masscanner(interface, rate, key, value, ms_targetfile)
			
			# DEV - version check.
			# Masscanner - Masscan version check.
			ms_currentversion = ms.get_version()
			if ms_currentversion == ms_stableversion:
				r.console.print(f'[italic grey37]Using Masscan version {ms_currentversion}\n')
			else:
				r.console.print(f'[red]Warning: Unsupported Masscan version {ms_currentversion} detected\n')
			
			# Masscanner - print cmd to stdout.
			print(ms.cmd)
			
			# Masscanner - launch scam.
			with r.console.status(spinner='bouncingBar', status=f'[status.text]Scanning {key.upper()}') as status:
				results = ms.run_scan()
				r.console.print(f'[grey37]{key.upper()}')

				# Sqlite - insert results (k:ipaddress, v[0]:port, v[1]:protocol, v[2]:description).
				for k, v in results.items():
					db.insert_masscanner(k, v[0], v[1], v[2])
					# Print results.
					r.console.print(f'{k}: {v[0]}')
				# r.console.print(f'[grey37]Completed:[/grey37] {key.upper()}\n')
		r.console.print('[bold gold3]All scans have completed!\n')

		# Sqlite - write database results to outputfile.
		for k, v in PORTSCANS.items():
			filepath = os.path.join(ms_dir, f'{k}.txt')
			results = db.get_ipaddress_by_description(k)
			if results != []:
				logging.info(f'Found results in databse.db via description: {k}')
				with open(filepath, 'w+') as f1:
					[f1.write(f'{result[0]}\n') for result in results]
					r.console.print(f'Results written to: {f1.name}')


	elif os.path.basename(configfile) == 'metasploit.ini':
		# Args - droptable
		if args.drop:
			db.drop_table('Metasploiter')
		# DEV # Args - inputlist
		inputlist = args.inputlist
		# ConfigParser - declare dict values.
		MSFMODULES = {k: v for k, v in config['msfmodules'].items()}
		# Sqlite - database init.
		db.create_table_metasploiter()
		
		# Header
		r.console.print(f'[italic grey37]Metasploit\n')
		
		for k, v in MSFMODULES.items():
			# DEV - convert to func. # FEATURE - support multiple ports.
			# Sqlite - fetch targets by filtering the metasploiter port (v).
			results = [i[0] for i in db.get_ipaddress_by_port(v)]
			logging.info(f'Found targets in databse.db via port: {v}')
			# Write targets to temp outputfile (targets are overwritten on each loop).
			with open(tmp_targetfile, 'w+') as f1:
				[f1.write(f'{i}\n') for i in results]
				logging.info(f'Targets written to: {f1.name}')
			
			# Metasploiter - instance init and run scan.
			metasploit = metasploiter.Metasploiter(k, v, tmp_targetfile)
			# Metasploiter - print cmd to stdout.
			print(metasploit.cmd)
			# Metasploiter - launch scan.
			results = metasploit.run_scan()
			r.console.print(f'[grey37]{os.path.basename(k.upper())}')
			
			# Regex - ipv4 pattern
			pattern = re.compile('''((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)''')
			# Regex -  find all matches for ipv4 addresses in metasploiter results.
			all_matches = re.finditer(pattern, results)
			# Sqlite - insert metasploiter results (match.group():ipaddress, k:msfmodule)
			for match in all_matches:
				db.insert_metasploiter(match.group(), os.path.basename(k))
				# Print metasploiter results to stdout.
				print(match.group())
			print('\n')
		r.console.print('[bold gold3]All scans have completed!\n')
		
		# Sqlite - write database results to outputfile.
		for k, v in MSFMODULES.items():
			filepath = os.path.join(nm_dir, f'{os.path.basename(k)}.txt')
			results = db.get_ipaddress_by_msfmodule(os.path.basename(k))
			if results != []:
				logging.info(f'Found results in databse.db via msfmodule: {os.path.basename(k)}')
				with open(filepath, 'w+') as f1:
					[f1.write(f'{result[0]}, {result[1]}\n') for result in results]
					r.console.print(f'Results written to: {f1.name}')


	elif os.path.basename(configfile) == 'nmap.ini':
		# Args - droptable
		if args.drop:
			db.drop_table('Nmapper')
		# ConfigParser - declare dict values.
		# NMCONFIG = {k: v for k, v in config['nmapconfig'].items()}
		NSESCANS = {k: v for k, v in config['nsescans'].items()}
		# Sqlite - databse init.
		db.create_table_nmapper()
		
		# Header
		r.console.print(f'[italic grey37]Nmap Scripting Engine Scanner')
		
		# Return - Nmap targetfile to disk.
		for k, v in NSESCANS.items():
			# FEATURE - support multiple ports.
			# Sqlite - fetch targets by filtering the nse-scan port (v).
			results = [i[0] for i in db.get_ipaddress_by_port(v)]
			logging.info(f'Found targets in databse.db via port: {v}')
			# Write targets to temp outputfile (targets are overwritten on each loop).
			with open(tmp_targetfile, 'w+') as f1:
				[f1.write(f'{i}\n') for i in results]
				logging.info(f'Targets written to: {f1.name}')
			
			# Nmapper - instance init and run scan.
			xmlfile = os.path.join(xml_dir, f'{k}.xml')
			nm = nmapper.Nmapper(k, v, tmp_targetfile, xmlfile)
			
			# DEV - version check.
			# Nmapmer - Nmap version check.
			nm_currentversion = nm.get_version()
			if nm_currentversion == nm_stableversion:
				r.console.print(f'[italic grey37]Using Nmap version {nm_currentversion}\n')
			else:
				r.console.print(f'[red]Warning: Unsupported Nmap version {nm_currentversion} detected\n')

			# Nmapper - print cmd to stdout.
			print(nm.cmd)
			
			# Nmapper - launch scam.
			r.console.print(f'[grey37]{k.upper()}')
			with r.console.status(spinner='bouncingBar', status=f'[status.text]Scanning {k.upper()}') as status:
				nm.run_scan()
			
				# XmlParse - instance init, read xmlfile and return results to database.
				xmlparse = xmlparser.NseParser()
				xmlresults = xmlparse.run(xmlfile)
				# DEV
				invalidresults = [None, 'Message signing enabled and required', 'required']
				# Omit positive results from database insertion and printing to stdout.
				for i in xmlresults:
					if i[1] != 'Message signing enabled and required' and i[1] != 'required':
						# Sqlite - insert xmlfile results (i[0]:ipaddress, i[2]:nsescript, i[1]:nseoutput).
						[db.insert_nmapper(i[0], i[2], i[1]) for i in xmlresults if i != None]
						# Print nse-scan results to stdout.
						r.console.print(f'{i[0]}: [red]{i[1].upper()}')

			# r.console.print(f'[grey37]Completed:[/grey37]\n')
		r.console.print('[bold gold3]All scans have completed!\n')

		# Sqlite - write database results to outputfile.
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
