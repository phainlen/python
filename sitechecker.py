#!/usr/bin/env python3

print ('''
  ______    _   _             ______  __                    __
.' ____ \  (_) / |_         .' ___  |[  |                  [  |  _
| (___ \_| __ `| |-'.---.  / .'   \_| | |--.  .---.  .---.  | | / ] .---.  _ .--.
 _.____`. [  | | | / /__\\ | |        | .-. |/ /__\\/ /'`\] | '' < / /__\\[ `/'`\]
| \____) | | | | |,| \__., \ `.___.'\ | | | || \__.,| \__.  | |`\ \| \__., | |
 \______.'[___]\__/ '.__.'  `.____ .'[___]|__]'.__.''.___.'[__|  \_]'.__.'[___]
''')

import requests,urllib,sys,csv
import pandas as pd

#disable SSL warnings from the requests library
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getInfo(resp,row,domain,domainlist,domain_reader):
    current_size = last_size = current_status = last_status = ""
    current_size = int(len(resp.content))
    last_size = int(getattr(row,'size'))

    current_status = resp.status_code
    last_status = getattr(row,'status') #row['status']

    #If the difference between the two sizes is greater than 100 bytes and the current size is greater than 100 bytes then report it
    if (current_size != last_size) and (abs(current_size - last_size) > 100) and (current_size > 100):
        print (domain + " * Changed size to " + str(current_size) + ".  Was " + str(last_size) + "\n")
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'size']=current_size
        df.to_csv(domainlist, index=False)
    #else:
    #    print ("         * Size hasn't changed for " + domain)
    #Status of 429 is related to too many requests.
    if (int(current_status) != int(last_status)) and (int(current_status != 429)):
        print (domain + " * Changed status to " + str(current_status) + ". Was " + str(last_status) + "\n")
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'status']=current_status
        df.to_csv(domainlist, index=False)
    #else:
    #    print ("         * Status hasn't changed for " + domain)

def main():
    if len(sys.argv)<2:
        print ('''Help: Usage:SiteChecker.py domain_list.txt''')
        print ('''Domain list should be in the format of:''')
        print ('''   domain,size,status''')
        print ('''*NOTE* All new domains in the list get a size and status of 0''')
        sys.exit(0)
    domainlist=sys.argv[1]
    #Read input file
    domain_reader = pd.read_csv(domainlist,index_col=0)
    #Iterate through domains
    for index,row in enumerate(domain_reader.itertuples()):
        domain = getattr(row, 'Index')
        #print ("- Analyzing the domain: " + domain + "\n")
        try:
            resp = ""
            resp = requests.get('http://' + domain,timeout=1,verify=False)
        except requests.exceptions.RequestException as e:
            #print("         * " + domain + ": Connection Error for http.")
            try:
                resp = ""
                resp = requests.get('https://' + domain,timeout=1,verify=False)
            except: # requests.exceptions.RequestException as e:
                #print("         * " + domain + ": Connection Error for https.")
                #If not successful getting http or https, then the site has no content (0)
                #write to the csv and move on to the next domain
                df = pd.read_csv(domainlist)
                df.loc[domain_reader.index.get_loc(domain),'size']=0
                df.loc[domain_reader.index.get_loc(domain),'status']=0
                df.to_csv(domainlist, index=False)
            else:
                getInfo(resp,row,domain,domainlist,domain_reader)

        else:
            getInfo(resp,row,domain,domainlist,domain_reader)

main()
