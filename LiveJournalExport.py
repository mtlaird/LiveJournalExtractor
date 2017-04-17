import requests
from bs4 import BeautifulSoup
import re
import csv
import os


class LiveJournalExport:
    def __init__(self):

        self.username = 'username'
        self.password = 'password'
        self.destination_directory = 'data'
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/57.0.2987.133 Safari/537.36'
        }
        self.logged_in = False

    def login(self):

        payload = {
            'returnto': '/export.bml',
            'user': self.username,
            'password': self.password,
            'action': 'login:'
        }

        response = self.session.post('http://www.livejournal.com/login.bml', headers=self.headers, data=payload)

        if response.status_code == 200:
            self.logged_in = True

    def export_month(self, year, month):

        url = 'http://www.livejournal.com/export_do.bml?authas={}'.format(self.username)

        payload = {
            'what': 'journal',
            'year': year,
            'month': month,
            'format': 'csv',
            'header': 'on',
            'encid': '2',
            'field_itemid': 'on',
            'field_eventtime': 'on',
            'field_logtime': 'on',
            'field_subject': 'on',
            'field_event': 'on',
            'field_security': 'on',
            'field_allowmask': 'on',
            'field_currents': 'on'
        }

        export_headers = self.headers

        export_headers['Content-Type'] = 'application/x-www-form-urlencoded'

        destination_filename = '{}-livejournal-entries-{}-{}.csv'.format(self.username, year, month)

        response = self.session.post(url, headers=self.headers, data=payload)

        if response.status_code != 200:
            return response  # This should raise an error

        with open(self.destination_directory + '/' + destination_filename, 'w') as dest_file:
            dest_file.write(response.content)

        return response

    def export_blog(self, start_year, end_year):

        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                print "Exporting {} {} ...".format(year, month)
                res = self.export_month(year, month)
                if res.status_code == 200:
                    print "Success!"
                else:
                    print "There was a problem."
                    print "Status code: {}".format(res.status_code)
                    print res.content

    def get_comments_from_post(self, post_id):

        url = 'http://{}.livejournal.com/{}.html'.format(self.username, post_id)

        res = self.session.get(url, headers=self.headers)

        if res.status_code != 200:
            return False

        soup = BeautifulSoup(res.text, 'html.parser')

        comment_divs = soup.find_all('div', {'id': re.compile('ljcmt')})

        post_comments = []

        for cd in comment_divs:
            comment = {'username': cd.find('span', {'class': 'ljuser'}).text,
                       'time': cd.find('th', text='Date:').next_sibling.text,
                       'content': ''.join(
                           [str(c) for c in cd.find('div', {'id': re.compile('cmtbar')}).next_sibling.contents]),
                       'post_id': post_id}
            post_comments.append(comment)

        return post_comments

    def write_comments_to_csv_file(self, comments, filename):

        file_path = self.destination_directory + '/' + filename
        with open(file_path, 'wb') as csv_file:

            csv_writer = csv.DictWriter(csv_file, fieldnames=['post_id', 'username', 'time', 'content'])
            if os.stat(file_path).st_size == 0:
                csv_writer.writeheader()
            csv_writer.writerows(comments)

    def get_post_ids_from_entry_file(self, filename):

        file_path = self.destination_directory + '/' + filename

        with open(file_path, 'r') as csv_file:
            ids = []
            reader = csv.DictReader(csv_file)
            for row in reader:
                ids.append(row['itemid'])

        return ids


class LiveJournalCsvReader:

    def __init__(self, month, year):

        self.destination_directory = 'entries'
        self.username = 'username'
        self.password = 'password'
        self.year = year
        self.month = month
        self.entries = []

    def read_entries(self):

        filename = '{}-livejournal-entries-{}-{}.csv'.format(self.username, self.year, self.month)
        file_path = self.destination_directory + '/' + filename

        with open(file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.entries.append(row)

    def get_entry_by_id(self, entry_id):

        for e in self.entries:
            if e['itemid'] == entry_id:
                return e

        return None
