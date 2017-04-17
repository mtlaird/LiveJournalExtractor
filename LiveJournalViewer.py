from flask import Flask
app = Flask(__name__)
import LiveJournalExport as lje
import csv


@app.route('/<string:username>/<int:year>/<int:month>')
def homepage(username, year, month):

    config = None

    with open('config.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                config = row

    if not config:
        return None

    reader = lje.LiveJournalCsvReader(month=month, year=year, config=config)
    reader.read_entries()
    retstr = ''

    for e in reader.entries:
        if e['subject']:
            retstr += '<p><b>{}</b></p>'.format(e['subject'])
        retstr += '<p><i>{}</i></p>'.format(e['eventtime'])
        retstr += '<div>{}</div>'.format(e['event']).replace('\n', '<br>')
        retstr += '<hr>'

    return retstr

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)


