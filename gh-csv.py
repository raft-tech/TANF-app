import csv
import json

gh_file = open('github-dump.json','r').readlines()
csv_file = open('github-dump.csv','w')

tickets = {}
for line in gh_file:
    data = json.loads(line.strip())
    data_number = data['number']
    tickets[data_number] = {
        'title': data['title'].strip(','),
        'author': data['author']['login'],
        'created_at': data['createdAt'],
        'url': data['url'],
        'epic': '',
    }


csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Number','Author','Created At','Title','URL','Epic'])
csv_writer.writerows([[num,v['author'],v['created_at'],v['title'],v['url'],v['epic']] for num,v in tickets.items()])