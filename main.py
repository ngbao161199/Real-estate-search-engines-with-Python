# Importing flask module in the project is mandatory 
# An object of Flask class is our WSGI application. 
from flask import Flask,render_template, request,redirect, url_for,flash, send_from_directory, jsonify, make_response
import json
import os
import pickle
import numpy
import csv
import pandas as pd
from py_approach import process

# Flask constructor takes the name of  
# current module (__name__) as argument. 
app = Flask(__name__) 

#Refresh cache
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response
  
# The route() function of the Flask class is a decorator,  
# which tells the application which URL should call  
# the associated function. 

result = []
link = []
score = []
leng = 0
detail = []

@app.route("/")
def index():
    return render_template("/html/home.html")

@app.route("/search")
def search():
    return render_template("/html/search.html", result=result, link = link,  score = score, detail = detail, leng = leng)

@app.route('/searchQuery',  methods=['POST'])
def getSearchQuery():
    q = (request.form['query'])
    result, link, score, detail = process.work(q)
    leng = len(result)
    return render_template('/html/search.html', q=q, result=result, link = link,  score = score, detail = detail, leng = leng)

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(use_reloader = True, debug=True, port=port)