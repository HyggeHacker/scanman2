# ScanMan User Guide

This guide provides detailed instructions and examples for using ScanMan, a comprehensive network reconnaissance and vulnerability scanning framework.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Scanning Modes](#scanning-modes)
3. [Understanding Results](#understanding-results)
4. [Advanced Usage](#advanced-usage)
5. [Troubleshooting](#troubleshooting)

## Quick Start

After installation, here are the most common ways to use ScanMan:

### Basic Network Scan

This will perform a basic network scan using Masscan:

```bash
python3 scanman.py -iL targets.txt
```

### Full Internal Penetration Test Scan

For a comprehensive scan that covers most scenarios during an internal penetration test:

```bash
python3 scanman.py -iL targets.txt -d example.local -m -n -eg -ew -k --ipparse --smbparse
```

This will:
- Scan targets in the list with Masscan
- Enumerate domain controllers for example.local
- Run Metasploit vulnerability checks
- Run Nmap vulnerability checks
- Test egress filtering
- Take screenshots of web services with EyeWitness
- Attempt Kerberos attacks (if domain controllers are found)
- Parse and extract IP addresses from results
- Filter out false positives for SMB signing

## Scanning Modes

### Port Scanning with Masscan

```bash
python3 scanman.py -iL targets.txt
```

This is the core functionality of ScanMan. It will scan all targets in the list for the ports configured in the `config.ini` file.

You can adjust the scan rate with the `-r` flag:

```bash
python3 scanman.py -iL targets.txt -r 500
```

### Domain Controller Discovery

```bash
python3 scanman.py --domain example.local
```

This will query DNS to locate domain controllers for the specified domain. You can provide multiple domains:

```bash
python3 scanman.py --domain example.local corp.local test.local
```

If you need to use a specific DNS server:

```bash
python3 scanman.py --domain example.local --nameserver 192.168.1.53
```

### Kerberos Attacks

The `-k` flag enables Kerberos attacks (requires the `-d` flag to specify a domain):

**With Domain Credentials:**

```bash
python3 scanman.py --domain example.local -k -u Administrator -p Password123
```

**With NTLM Hash (Pass-the-Hash):**

```bash
python3 scanman.py --domain example.local -k -u Administrator -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
```

**With User File for AS-REP Roasting:**

```bash
python3 scanman.py --domain example.local -k --userfile users.txt
```

**Anonymous Attempt:**

```bash
python3 scanman.py --domain example.local -k
```

### Vulnerability Scanning

To enable Nmap vulnerability scanning:

```bash
python3 scanman.py -iL targets.txt --nmap
```

To enable Metasploit vulnerability scanning:

```bash
python3 scanman.py -iL targets.txt --msf
```

You can combine both:

```bash
python3 scanman.py -iL targets.txt --nmap --msf
```

### Web Service Screenshots

```bash
python3 scanman.py -iL targets.txt --eyewitness
```

To specify a custom output directory:

```bash
python3 scanman.py -iL targets.txt --eyewitness --ewreport /path/to/report
```

### Egress Filtering Test

```bash
python3 scanman.py --egress
```

This will test for outbound connectivity on common ports to help identify egress filtering.

## Understanding Results

ScanMan organizes results by tool and service in the `results` directory:

- `results/masscan/`: Contains port scan results
- `results/nmap/`: Contains Nmap vulnerability scan results
- `results/metasploit/`: Contains Metasploit vulnerability scan results
- `results/dc/`: Contains domain controller information
- `results/kerberos/`: Contains Kerberos attack results
- `results/eyewitness/`: Contains web screenshots
- `results/egress/`: Contains egress filtering test results

All results are also stored in a SQLite database (default: `.scanman.db`), which can be queried for more detailed analysis.

### Database Tables

- `Masscan`: Port scan results
- `Nmap`: Nmap vulnerability scan results
- `Metasploit`: Metasploit vulnerability scan results
- `DomainController`: Domain controller information
- `Kerberos`: Kerberos attack results

## Advanced Usage

### Custom Database Location

```bash
python3 scanman.py -iL targets.txt --database /path/to/database.db
```

### Clearing the Database

```bash
python3 scanman.py --droptables
```

### Logging Levels

```bash
python3 scanman.py -iL targets.txt --loglevel DEBUG
```

Available levels: DEBUG, INFO, WARNING (default)

### Customizing Scans

Edit the `configs/config.ini` file to customize:

- Ports to scan for each service
- NSE scripts to run
- Metasploit modules to use
- EyeWitness settings
- Kerberos attack options
- Egress scan targets

## Troubleshooting

### No Targets Found for Vulnerability Scanning

This typically means that Masscan didn't find any hosts with the ports required for the vulnerability scans. Try running just the Masscan phase first to confirm ports are open:

```bash
python3 scanman.py -iL targets.txt
```

### Kerberos Attacks Failing

- Ensure the domain is reachable and domain controllers are accessible
- Verify credentials if using authenticated scans
- Check that Impacket tools are installed and in the PATH

### EyeWitness Errors

- Ensure EyeWitness is installed and the path in `config.ini` is correct
- Verify that the required dependencies for EyeWitness are installed

### Port Scans Taking Too Long

- Reduce the number of ports being scanned in `config.ini`
- Increase the scan rate with the `-r` flag (e.g., `-r 500`)
- Use a smaller target list

### Database Errors

If you encounter database errors, try clearing the tables:

```bash
python3 scanman.py --droptables
```

Or specify a new database file:

```bash
python3 scanman.py -iL targets.txt --database new_scan.db
```
