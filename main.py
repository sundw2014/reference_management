from flask import Flask, request, redirect, render_template, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
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

# Work = namedtuple('Work', ['title', 'bibtex', 'keywords', 'author', 'booktitle', 'year'])

app = Flask(__name__)
auth = HTTPBasicAuth()

with open('passwd') as f:
    passwd = f.readlines()

# import ipdb; ipdb.set_trace()

users = {
    passwd[0].strip(): generate_password_hash(passwd[1].strip())
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route('/_confirm', methods = ['POST'])
@auth.login_required
def _confirm():
    bibtex = request.form['bibtex']
    title = request.form['title']
    fname = request.form['fname']
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
    w = {'fname':fname, 'title':title, 'bibtex':bibtex, 'keywords':keywords, 'author':author.split(' and '), 'booktitle':booktitle, 'year':year}
    literature.insert_one(w)

    return redirect('/create')

@app.route('/_createnew', methods = ['POST'])
@auth.login_required
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
    return render_template('confirm.html', fname=fname, bibtex=bibtex, title=title, author=author, booktitle=booktitle, year=year, available_keywords=json.dumps(available_keywords))

@app.route('/create')
@auth.login_required
def create():
    return render_template('create.html')

@app.route('/search')
@auth.login_required
def search():
    references = [{'fname':w['fname'], 'title':w['title'], 'bibtex':w['bibtex'], 'keywords':w['keywords'], 'author':w['author'], 'booktitle':w['booktitle'], 'year':w['year']} for w in literature.find({})]
    return render_template('search.html', references = json.dumps(references))

@app.route('/')
@auth.login_required
def hello_world():
    return 'Hello, World!'

@app.route('/upload/<path:path>')
@auth.login_required
def send_uploaded_files(path):
    return send_from_directory('upload', path)
