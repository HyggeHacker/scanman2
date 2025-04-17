# ScanMan

![Supported Python versions](https://img.shields.io/badge/python-3.9-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

ScanMan operates as a network reconnaissance and vulnerability scanner that combines multiple powerful security tools:

- **Masscan**: For fast port discovery
- **Nmap**: For vulnerability scanning via NSE scripts
- **Metasploit**: For vulnerability verification
- **EyeWitness**: For web service screenshots
- **Kerberos Attack Tools**: For Active Directory assessments

All results are stored in a SQLite database for easy querying and correlation.

## Overview

This Python3-based wrapper was developed to streamline the initial "scanning" phase of an internal network penetration test by integrating multiple security tools with a shared database and preconfigured command-line arguments.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/scanman.git
cd scanman
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Ensure the following tools are installed on your system:
   - Masscan
   - Nmap
   - Metasploit Framework
   - EyeWitness
   - Impacket (for Kerberos attacks)

## Usage

ScanMan supports multiple scanning modes, which can be used individually or combined:

### Basic Port Scanning

```bash
python3 scanman.py -iL targets.txt
```

This will perform port scans using Masscan on the specified targets.

### Vulnerability Scanning with Nmap and Metasploit

```bash
python3 scanman.py -iL targets.txt --nmap --msf
```

This will first run Masscan for port discovery, then use Nmap and Metasploit to check for vulnerabilities on the discovered services.

### Domain Controller Enumeration

```bash
python3 scanman.py --domain example.local
```

This will locate and enumerate domain controllers for the specified domain.

### Kerberos Attacks

For Kerberoasting and AS-REP Roasting attacks against Active Directory:

```bash
# With domain credentials
python3 scanman.py --domain example.local -k -u username -p password

# Using pass-the-hash with NTLM hashes
python3 scanman.py --domain example.local -k -u username -H HASH

# With a list of users for AS-REP Roasting
python3 scanman.py --domain example.local -k --userfile users.txt

# Anonymous attempt (less likely to succeed)
python3 scanman.py --domain example.local -k
```

### Web Service Screenshots with EyeWitness

```bash
python3 scanman.py -iL targets.txt --eyewitness
```

### Egress Filtering Test

```bash
python3 scanman.py --egress
```

### Typical Full-Spectrum Scan

```bash
python3 scanman.py -iL targets.txt -d example.local -m -n -eg -ew -k --ipparse --smbparse
```

## Command-Line Arguments

### Masscan Arguments
- `-iL, --inputlist`: Input from list of IPs/networks (**Enables Masscan**)
- `-eL, --excludefile`: Exclude list from file
- `-i, --interface`: Network adapter interface (default: eth0)
- `-r, --rate`: Masscan's rate in kpps (default: 250)

### Scanman Arguments
- `-m, --msf`: Enable MSF Vulnscans
- `-n, --nmap`: Enable Nmap Vulnscans
- `-eg, --egress`: Enable Egress-scan
- `-ew, --eyewitness`: Enable Eyewitness w/ portscans
- `-db, --database`: Filepath for Scanman database
- `--droptables`: Drop all database tables
- `--ipparse`: Enable IP address parsing
- `--smbparse`: Parse out false positives for SMB-signing
- `--loglevel`: Set logging level {DEBUG, INFO, WARNING}

### EyeWitness Arguments
- `-ewr, --ewreport`: EyeWitness report output directory

### Domain Controller Arguments
- `-d, --domain`: Provide domain name(s) (**Enables GetDC**)
- `-ns, --nameserver`: Nameserver
- `-k, --kerberos`: Enable Kerberos attacks (Kerberoasting, AS-REP Roasting)
- `-u, --username`: Username for Kerberos authentication
- `-p, --password`: Password for Kerberos authentication
- `-H, --hash`: NTLM hash for pass-the-hash authentication
- `--userfile`: File containing usernames for AS-REP Roasting

## Configuration

Most tool-specific settings can be customized in the `configs/config.ini` file:

- Ports to scan for each service
- NSE scripts to run
- Metasploit modules to use
- EyeWitness settings
- Kerberos attack options
- Egress scan targets

## Output

Results are stored in the following directories:

- `results/masscan/`: Masscan results
- `results/nmap/`: Nmap vulnerability scan results
- `results/metasploit/`: Metasploit vulnerability scan results
- `results/dc/`: Domain controller information
- `results/kerberos/`: Kerberos attack results
- `results/eyewitness/`: Web service screenshots
- `results/egress/`: Egress filtering test results

All results are also stored in a SQLite database for easy querying and correlation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

ScanMan is developed and maintained by Nick Sanzotta.

## Disclaimer

This tool is intended for legal security testing with proper authorization only. Unauthorized scanning or testing of networks is illegal and unethical.
