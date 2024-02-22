#!/user/bin/python 

'''
This script is for downloading the gene sequence based on the EC number.
In this version, just fill/change the EC unmber you interest in the script as followed:

EC = ["1.6.99.1", "1.3.1.31", "1.3.1.74", "1.3.1.48", "1.1.1.208"]

Run this script, then it will download the amino acid sequence. It will need some time as it can't be possible to access KEGG database high frequently.
'''

import urllib3
import time
import random

# Define a list of user agents to mimic different browsers
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    # Add more user agents if needed
]

# Function to get a random user-agent header
def get_random_user_agent():
    return random.choice(user_agents)

http = urllib3.PoolManager()
#put the EC unmber you interest
EC = ["1.6.99.1", "1.3.1.31", "1.3.1.74", "1.3.1.48", "1.1.1.208"]
#EC = ["K00359"] #actually for KO
for ECNUM in EC:
    r = http.request('GET', 'http://rest.kegg.jp/get/ec:%s/' % ECNUM)
    #r = http.request('GET', 'http://rest.kegg.jp/get/ko:%s/' % ECNUM)  #for KO
    lines_tmp = r.data.decode().split('\n')
    lines = []
    swc = False
    for line in lines_tmp:
        if line.startswith('GENES'):
            swc = True
        if not swc:
            continue
        if swc and (not line.startswith(' ')) and (not line.startswith('GENES')):
            break
        lines.append(line[12:].strip())

    org_ids = []
    for line in lines:
        tmp = line.split(' ')
        org = tmp[0].replace(':', '').lower()
        ids = [i.split('(')[0] for i in tmp[1:]]
        org_ids += [(org, i) for i in ids]
    print('%s gene AA seq to collect...' % len(org_ids))

    fout = open('tmp_EC_%s.fastq' % ECNUM, 'w')
    for num, (org, i) in enumerate(org_ids):
        if num % 500 == 0:
            print('{:.2%}'.format(num / len(org_ids)) + ' done.')

        # Add a delay between requests (e.g., 0.1-0.5 seconds)
        time.sleep(random.uniform(0.1, 0.5))

        try:
            headers = {'User-Agent': get_random_user_agent()}
            r = http.request('GET', 'http://rest.kegg.jp/get/%s:%s/aaseq' % (org, i), headers=headers)
            seq = r.data.decode()
            fout.write(seq + '\n')
        except Exception as e:
            continue

    fout.close()
