from . import document
from flask import render_template

@document.route('/geneMapping/', methods=['GET'])
def geneMapping():
    return render_template('document/geneMapping.html')


@document.route('/dataAnalysis/', methods=['GET'])
def dataAnalysis():
    return render_template('document/dataAnalysis.html')


@document.route('/dataSharing/', methods=['GET'])
def dataSharing():
    return render_template('document/dataSharing.html')

@document.route('/contactUS/', methods=['GET'])
def contactUS():
    return render_template('document/contactUS.html')

@document.route('/cite/', methods=['GET'])
def cite():
    return render_template('document/cite.html')
