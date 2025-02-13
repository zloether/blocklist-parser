#!/usr/bin/env python

###############################################################################################
# NAME: blocklist-parser.py
# 
# Website: https://github.com/zloether/blocklist-parser
#
# Description: Parser for block lists
###############################################################################################


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import re
import argparse
import requests
import tldextract


# -----------------------------------------------------------------------------
# variables
# -----------------------------------------------------------------------------
hagezi_dns_blocklists_domains = 'https://api.github.com/repos/hagezi/dns-blocklists/contents/domains'
domain_regex = r'(?<![a-z0-9-])([a-z0-9-]{1,63}\.)+[a-z]{2,63}(?![a-z0-9-])'

# -----------------------------------------------------------------------------
# help text
# -----------------------------------------------------------------------------
help_description = '''
Downloads and parses simplified block lists
'''


# -----------------------------------------------------------------------------
# functions
# -----------------------------------------------------------------------------

# validate domain name
def is_valid_domain_name(domain_string):
    validator = re.compile(domain_regex, re.IGNORECASE)
    
    if validator.match(domain_string):
        return True
    else:
        return False


# read provided file
def read_file(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.readlines()
            return content
    
    else:
        print(f'Cannot find file: {file_path}')
        exit()


# download list of supported blocklists
def list_blocklists():
    resp = requests.get(hagezi_dns_blocklists_domains)
    j = resp.json()

    output = {}
    for item in j:
        name = item['name']
        url = item['download_url']

        # make the names friendlier
        name = name.replace('.txt', '') # remove file extension
        name = name.replace('native.', '') # remove "native"

        output[name] = url
    
    return output


# parse provided list of domains
def parse_blocklist(blocklist):
    content = []
    for line in blocklist:
        line = line.strip()

        # remove leading zero IP
        if line.startswith('0.0.0.0 '):
            line = line.replace('0.0.0.0 ', '')
        
        # skip comment lines or blank lines
        if line.startswith('#') or line == '' or not is_valid_domain_name(line):
            continue

        # extract TLD from line
        domain = tldextract.extract(line).registered_domain
        
        if domain not in content:
            content.append(domain)
    
    return content


# download and parse blocklist
def download_and_parse_blocklist(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f'Error ({resp.status_code}) connecting to URL: {url}')
        exit()

    content = resp.text.splitlines()

    return parse_blocklist(content)


# read and parse blocklist
def read_and_parse_blocklist(file_path):
    file_contents = read_file(file_path)

    return parse_blocklist(file_contents)
    


# Configure argument parser
def __parse_arguments():
    # create parser object
    parser = argparse.ArgumentParser(description=help_description)
    
    # setup argument to store blocklist name
    parser.add_argument('-b', '--blocklist',
                        metavar='<name>', action='store',
                        help='Name of the blocklist to use')
    
    # setup argument to store blocklist file
    parser.add_argument('-f', '--file',
                        metavar='<file>', action='store',
                        help='Blocklist file to use')

    # setup argument to output list of supported blocklists
    parser.add_argument('-l', '--list', default=None,
                        action='store_true',
                        help='List supported blocklists')
    
    # setup argument to store blocklist URL
    parser.add_argument('-u', '--url',
                        metavar='<url>', action='store',
                        help='URL of blocklist to use')


    # parse the arguments
    args = parser.parse_args()
    
    return args, parser


# Main function
def __run_main():
    args, parser = __parse_arguments()

    if args.list:
        list_of_blocklists = list_blocklists()
        list_names = list(list_of_blocklists.keys())
        print('\n'.join(list_names))
    
    elif args.blocklist:
        list_of_blocklists = list_blocklists()
        if args.blocklist in list_of_blocklists.keys():
            parsed = download_and_parse_blocklist(list_of_blocklists[args.blocklist])
            print('\n'.join(parsed))
    
    elif args.url:
        parsed = download_and_parse_blocklist(args.url)
        print('\n'.join(parsed))
    
    elif args.file:
        parsed = read_and_parse_blocklist(args.file)
        print('\n'.join(parsed))

    else:
        parser.print_help()

# -----------------------------------------------------------------------------
# Run interactively
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    __run_main()