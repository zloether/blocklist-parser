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
import argparse
import requests
import json


# -----------------------------------------------------------------------------
# variables
# -----------------------------------------------------------------------------
hagezi_dns_blocklists_domains = 'https://api.github.com/repos/hagezi/dns-blocklists/contents/domains'


# -----------------------------------------------------------------------------
# help text
# -----------------------------------------------------------------------------
help_description = '''
Downloads and parses simplified block lists
'''


# -----------------------------------------------------------------------------
# functions
# -----------------------------------------------------------------------------


def list_blocklists():
    resp = requests.get(hagezi_dns_blocklists_domains)
    j = resp.json()

    output = {}
    for item in j:
        name = item['name']
        url = item['html_url']

        # make the names friendlier
        name = name.replace('.txt', '') # remove file extension
        name = name.replace('native.', '') # remove "native"

        output[name] = url
    
    return output


# Configure argument parser
def __parse_arguments():
    # create parser object
    parser = argparse.ArgumentParser(description=help_description)
    
    # setup argument to store blocklist name
    parser.add_argument('-b', '--blocklist', nargs=1, default='-',
                        metavar='blocklist', action='store',
                        help='Name of the blocklist to use')

    # setup argument to output list of supported blocklists
    parser.add_argument('-l', '--list', default=None,
                        action='store_true',
                        help='List supported blocklists')
    
    # setup argument to store blocklist URL
    parser.add_argument('-u', '--url',
                        metavar='url', action='store',
                        help='URL of blocklist to use')


    # parse the arguments
    args = parser.parse_args()
    
    return args


# Main function
def __run_main():
    args = __parse_arguments()

    if args.list:
        list_of_blocklists = list_blocklists()
        list_names = list(list_of_blocklists.keys())
        print('\n'.join(list_names))



# -----------------------------------------------------------------------------
# Run interactively
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    __run_main()