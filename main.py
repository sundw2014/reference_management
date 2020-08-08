from flask import Flask, request, redirect, render_template
import pymongo
import bibtexparser
# from scholarly import scholarly
from os import path
from collections import namedtuple
import time
import json

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['literature']
literature = db['literature']
# keywords = db['keywords']

Work = namedtuple('Work', ['title', 'bibtex', 'keywords', 'author', 'booktitle', 'year'])

app = Flask(__name__)

@app.route('/_confirm', methods = ['POST'])
def _confirm():
    bibtex = request.form['bibtex']
    title = request.form['title']
    author = request.form['author']
    booktitle = request.form['booktitle']
    year = request.form['year']
    # import ipdb; ipdb.set_trace()
    keywords = request.form.getlist('keywords[]')
    # upload to google drive
    # output = subprocess.check_output('gdrive upload --parent 1QZvSi74TytnGUjfMll6Qbhf9MZrrLG_i --name %s.pdf file.pdf'%title, universal_newlines=True, shell=True)
    # file_id = output.split(' ')[1]
    # output = subprocess.check_output('gdrive info %s'%file_id, universal_newlines=True, shell=True)
    # view_url, download_url = output.splitlines(False)[-2:]
    # view_url = view_url.split(':')[1][1:]
    # download_url = download_url.split(':')[1][1:]
    # save to db
    w = {'title':title, 'bibtex':bibtex, 'keywords':keywords, 'author':author.split(' and '), 'booktitle':booktitle, 'year':year}
    literature.insert_one(w)

    return redirect('/createnew')

@app.route('/_createnew', methods = ['POST'])
def _createnew():
    file = request.files['fileToUpload']

    # title = request.form['title']
    bibtex = request.form['bibtex']
    # from IPython import embed;embed()
    # import ipdb; ipdb.set_trace()
    # if bibtex == '':
    #     query = scholarly.search_pubs(title)
    #     pub = next(query)
    #     bibtex = pub.bibtex
    parsed_bibtex = bibtexparser.loads(bibtex).entries[0]
    title = parsed_bibtex['title']
    author = parsed_bibtex['author']
    booktitle = None
    if 'booktitle' in parsed_bibtex:
        booktitle = parsed_bibtex['booktitle']
    elif 'journal' in parsed_bibtex:
        booktitle = parsed_bibtex['journal']
    elif 'publisher' in parsed_bibtex:
        booktitle = parsed_bibtex['publisher']
    year = parsed_bibtex['year']

    # save
    fname = 'upload/' + title+'.pdf'
    if path.exists(fname):
        fname = 'upload/' + title + '___' + str(time.time()) + '.pdf'
    file.save(fname)

    # import ipdb; ipdb.set_trace()
    available_keywords = list(set(sum([w['keywords'] for w in literature.find({})], [])))

    # extracted info
    return render_template('confirm.html', bibtex=bibtex, title=title, author=author, booktitle=booktitle, year=year, available_keywords=json.dumps(available_keywords))

@app.route('/createnew')
def createnew():
    return render_template('createnew.html')

@app.route('/')
def hello_world():
    return 'Hello, World!'
