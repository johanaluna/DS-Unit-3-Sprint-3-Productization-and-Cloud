"""OpenAQ Air Quality Dashboard with Flask."""
# 0. imports
from flask import Flask, render_template
import requests
import openaq
from flask_sqlalchemy import SQLAlchemy

# 1. instantiate app
APP = Flask(__name__)

# 2. Connect to sqlite and create database
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

# Class Record
class Record(DB.Model):
    """with this class we extract the data from the API """
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return "Time{} : Value{}".format(self.datetime,self.value)


# function to extract data
def raw_data(city, parameter):
    """
    1. created object api that have the class OpenAQ
    2. api.measurements return two values status and body
    3. return the list of tuples with a loop
    """
    api = openaq.OpenAQ()
    status, body = api.measurements(city=city, parameter=parameter)
    return [(n['date']['utc'], n['value']) for n in body['results']]

# Routes
@APP.route('/')
def root():
    """Base View"""
    """show the records equals or bigger than 10"""
    return str(Record.query.filter(Record.value >= 10.0).all())

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    #loop to add new data
    for n in raw_data('Los Angeles', 'pm25'):
        record_data = Record(datetime = str(n[0]), value = n[1])
        DB.session.add(record_data)
    DB.session.commit()
    return 'Data refreshed!'


# Run App
if __name__ == '__main__':
    APP.run(debug=True)
