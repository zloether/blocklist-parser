# blocklist-parser
Parser for block lists that provides a simplified list of registered domains that can be blocked instead of a long list of FQDNs.


## Table of Contents
- [Setup](#setup)
- [Usage](#usage)
- [Disclaimer](#disclaimer)
- [License](#license)


## Setup
1. Have python3 installed (instructions)[https://realpython.com/installing-python/]
1. Clone the repository
    ```
    git clone https://github.com/zloether/blocklist-parser.git
    ```
1. Switch to the cloned directory
    ```
    cd blocklist-parser
    ```
1. Install depenency packages
    ```
    python3 -m pip install -r requirements.txt
    ```


## Usage
```
blocklist-parser.py -h                    
usage: blocklist-parser.py [-h] [-b blocklist] [-l] [-u url]

Downloads and parses simplified block lists

options:
  -h, --help            show this help message and exit
  -b, --blocklist <name>
                        Name of the blocklist to use
  -l, --list            List supported blocklists
  -u, --url url         URL of blocklist to use
```


## Disclaimer
The simplified list of domains produced may include domains for commonly used content delivery networks (CDNs) that, if blocked, will likely break things on your network. Always validate the resultant list and use at your own risk.


## License

This project is licensed under the MIT License