#!/opt/homebrew/bin/python3

import csv
import json
import subprocess
from datetime import datetime

# Prioritized csv from last time
prioritized_csv_file = open('github-dump-old.csv','r')  # TODO: take filename as input
old_tickets = {}
for line in prioritized_csv_file:
    data = line.strip().split(',')
    if data[0] == 'Priority':
        continue # skip first line
    old_priority = int(data[0])
    number = int(data[1])
    old_tickets[number] = old_priority
prioritized_csv_file.close()

# make subprocess call to run `gh-issues.bash` script
subprocess.run(['./gh-issues.bash'])
gh_file = open('github-dump.json','r').readlines()

tickets = {}
for line in gh_file:
    #print(line)
    data = json.loads(line.strip())
    data_number = data['number']
    tickets[data_number] = {
        'title': data['title'].strip(','),
        'author': data['author']['login'],
        'created_at': data['createdAt'],
        'url': data['url'],
        'epic': '',
    }

short_date = datetime.now().strftime("%b-%d-%H:%M")  # e.g., Dec-5-15:30
csv_file = open('github-dump-' + short_date + '.csv','w') # TODO: add date to filename
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Priority', 'Number','Author','Created At','Title','URL','Epic'])

print(old_tickets.items())
view = [ (k,v) for k,v in old_tickets.items() ]

for num,rank in view:
    try:
        v = tickets[num]
        csv_writer.writerow([rank, num, v['author'],v['created_at'],v['title'],v['url'],v['epic']])
    except KeyError:
        continue

csv_file.close()