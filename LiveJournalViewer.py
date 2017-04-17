from flask import Flask
app = Flask(__name__)
import LiveJournalExport as lje


@app.route('/<int:year>/<int:month>')
def homepage(year, month):

    reader = lje.LiveJournalCsvReader(month=month, year=year)
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


