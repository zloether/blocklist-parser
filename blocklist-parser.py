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
script_dir = os.path.dirname(os.path.realpath(__file__))
cdn_file = os.path.join(script_dir, 'cdn-domains.txt')
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


# cleans a list to make sure it only contains domain names
def clean_list(input_list, intact_list=None, extract_tld=True):
    output = []

    for item in input_list:
        # remove leading or trailing non-printing characters
        item = item.strip()

        # remove leading zero IP
        if item.startswith('0.0.0.0 '):
            item = item.replace('0.0.0.0 ', '')
        
        # skip comment lines or blank lines
        if item.startswith('#') or item == '' or not is_valid_domain_name(item):
            continue
        
        # extract TLD from line
        if extract_tld:
            domain = tldextract.extract(item).registered_domain
        else:
            domain = item

        # check if domain is in the list to leave intact (includes subdomains in output)
        if intact_list:
            if domain in intact_list:
                domain = item

        if domain not in output:
            output.append(domain)
    
    return output


# parse provided list of domains
def parse_list(input_list, ignore_list=None, intact_list=None, extract_tld=True):
    blocklist = clean_list(input_list, intact_list=intact_list, extract_tld=extract_tld)

    content = []
    for item in blocklist:
        
        if ignore_list:
            if item in ignore_list:
                continue

        if item not in content:
            content.append(item)
    
    return content


# download and parse blocklist
def download_and_parse_list(url, ignore_list=None, intact_list=None):
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f'Error ({resp.status_code}) connecting to URL: {url}')
        exit()

    content = resp.text.splitlines()

    return parse_list(content, ignore_list=ignore_list, intact_list=intact_list)


# read and parse blocklist
def read_and_parse_list(file_path, ignore_list=None, intact_list=None):
    file_contents = read_file(file_path)

    return parse_list(file_contents, ignore_list=ignore_list, intact_list=intact_list)


# reads list of CDNs
def get_cdn_list(target_file=cdn_file):
    cdns = read_file(target_file)
    return parse_list(cdns)


# Configure argument parser
def __parse_arguments():
    # create parser object
    parser = argparse.ArgumentParser(description=help_description)
    
    # setup argument to store blocklist name
    parser.add_argument('-b', '--blocklist',
                        metavar='<name>', action='store',
                        help='Name of the blocklist to use')
    
    # setup argument to handle CDNs from a provided list
    parser.add_argument('-c', '--cdn-file',
                        metavar='<file>', action='store',
                        dest='cdn_file',
                        help='CDN file to use')

    # setup argument to store blocklist file
    parser.add_argument('-f', '--file',
                        metavar='<file>', action='store',
                        help='Blocklist file to use')
    
    # setup argument to ignore domains
    parser.add_argument('-i', '--ignore',
                        metavar='<file>', action='store',
                        dest='ignore_file',
                        help='Ignore file to use')

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
    output = None

    ignore_list = None
    intact_list = None

    # handler for ignore list
    if args.ignore_file:
        print(f'Loading ignore list from file: {args.ignore_file}')
        ignore_list = parse_list(read_file(args.ignore_file), extract_tld=False)
    
    # handler for CDNs list
    if args.cdn_file:
        print(f'Loading CDN list from file: {args.cdn_file}')
        intact_list = get_cdn_list(args.cdn_file)
    else:
        intact_list = get_cdn_list()

    if args.list:
        list_of_blocklists = list_blocklists()
        output = list(list_of_blocklists.keys())
    
    elif args.blocklist:
        list_of_blocklists = list_blocklists()
        if args.blocklist in list_of_blocklists.keys():
            output = download_and_parse_list(list_of_blocklists[args.blocklist], ignore_list=ignore_list, intact_list=intact_list)
        else:
            print(f'Unsupport blocklist name: {args.blocklist}')
    
    elif args.url:
        output = download_and_parse_list(args.url, ignore_list=ignore_list, intact_list=intact_list)
    
    elif args.file:
        output = read_and_parse_list(args.file, ignore_list=ignore_list, intact_list=intact_list)

    else:
        parser.print_help()
    
    if output:
        print('\n'.join(output))

# -----------------------------------------------------------------------------
# Run interactively
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    __run_main()