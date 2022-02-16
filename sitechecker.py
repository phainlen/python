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
    #Get current site info
    current_size = last_size = current_status = last_status = ""
    current_size = int(len(resp.content))
    current_status = resp.status_code

    #Get site info from csv file
    last_size = int(getattr(row,'size'))
    last_status = getattr(row,'status')
    last_desc = getattr(row,'desc')

    #If the difference between the two sizes is greater than 100 bytes and the current size is greater than 1000 bytes then report it
    #If the percentage difference is greater than 5% then print out the results to the screen otherwise there were nominal changes to the site that don't require a manual look
    if (current_size != last_size) and (abs(current_size - last_size) > 100) and (current_size > 1000):
        pct_diff = 0
        if (current_size > 0):
            pct_diff = last_size / current_size
        if ((pct_diff <= .95) or (pct_diff >= 1.05)):
            print (domain + " * Changed size to " + str(current_size) + ".  Was " + str(last_size) + "\n")
        #regardless of the percentage difference, we still want to record the size
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'size']=current_size
        df.to_csv(domainlist, index=False)
    #record the current size, just don't alert on the size change
    elif (current_size < 1000) or (abs(current_size - last_size < 100)):
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'size']=current_size
        df.to_csv(domainlist, index=False)
    #The corporate default splash page is 175600 bytes.
    if (current_size == 175600):
        print (domain + " * Same byte size as the corporate splash page.\n")

    #Look for parked page key words in the content
    if (("park" in str(resp.content)) and str(last_desc) != "parked"):
        print (domain + " * Contains the word 'park' in the content.  Potentially parked.\n")
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'desc']="parked"
        df.to_csv(domainlist, index=False)
    elif (("sale" in str(resp.content)) and str(last_desc) != "forsale"):
        print (domain + " * Contains the word 'sale' in the content.  Potentially for sale.\n")
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'desc']="forsale"
        df.to_csv(domainlist, index=False)

    #A status of 429 means that you have issued too many requests to the site.
    if (int(current_status) != int(last_status)) and (int(current_status != 429)):
        print (domain + " * Changed status to " + str(current_status) + ". Was " + str(last_status) + "\n")
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'status']=current_status
        df.to_csv(domainlist, index=False)

    #If the description is blank, then it is most likely a live site.
    if (str(last_desc) == ""):
        df = pd.read_csv(domainlist)
        df.loc[domain_reader.index.get_loc(domain),'desc']="live"
        df.to_csv(domainlist,index=False)

def main():
    if len(sys.argv)<2:
        print ('''Help: Usage:SiteChecker.py domain_list.txt''')
        print ('''Domain list should be in the format of:''')
        print ('''   domain,size,status,desc''')
        print ('''*NOTE* All new domains in the list get a size and status of 0''')
        print ('''*      Example new row in text file: newdomain.com,0,0,''')
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
                df.loc[domain_reader.index.get_loc(domain),'desc']="dead"
                df.to_csv(domainlist, index=False)
            else:
                getInfo(resp,row,domain,domainlist,domain_reader)

        else:
            getInfo(resp,row,domain,domainlist,domain_reader)

main()

#Get the top 10 domains by size
#cat domains.txt | grep -v "forsale" | grep -v "parked" | awk -F',' '{print $1, $2}' | sort -nk2 | tail -n 20
