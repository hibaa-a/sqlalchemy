# importing dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import numpy as np
import datetime as dt

# setting up the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflecting an existing database into a new model
Base = automap_base()

# reflecting the tables
Base.prepare(engine, reflect=True)

# saving the reference to the tables
measurement = Base.classes.measurement
station = Base.classes.station

# setting up Flask
app = Flask(__name__)

# Flask routes - starting at homepage and listing all available routes
@app.route('/')
def welcome():
    return (
        f'Welcome!<br>'
        f'Available routes:<br>'
        f'/api/v1.0/precipitation<br>'
        f'/api/v1.0/stations<br>'
        f'/api/v1.0/tobs<br>'
        f'/api/v1.0/<start><br>'
        f'/api/v1.0/<start>/<end><br>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # creating session
    session = Session(engine)
    # querying the precipitation measurements table
    result = session.query(measurement.date, measurement.prcp).all()
    # closing session
    session.close()
    # creating a list for precipitation measurements
    prcp1 = []
    for date, prcp in result:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp1.append(prcp_dict)
        return jsonify(prcp1)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    result2 = session.query(station.station).distinct().all()
    session.close()

    station_list = list(np.ravel(result2))
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    # most recent data point
    recent_date = dt.date(2017,8,23)
    # calculating the data one year from the most recent date
    query_date = recent_date - dt.timedelta(days=365)
    # querying tobs fot the most active station in the last year
    query1 = session.query(measurement.date, measurement.prcp).filter(measurement.date >= query_date).all()
    session.close()

    temp_list = []
    for date, tobs in query1:
        tobs_dict = {}
        tobs_dict[date] = tobs
        temp_list.append(tobs_dict)
    return jsonify(temp_list)

@app.route('/api/v1.0/<start>')
def start_date(start):
    session = Session(engine)

    query_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    temp_list = [func.min(measurement.tobs),
                func.max(measurement.tobs),
                func.avg(measurement.tobs)]

    date_temp = session.query(*temp_list).filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).all()

    session.close()

    return (
        f"Analysis of temperature from {start} to 2017-08-23:<br/>"
        f"Minimum temperature: {date_temp[0][0]} °F<br/>"
        f"Maximum temperature: {date_temp[0][1]} °F<br/>"
        f"Average temperature: {date_temp[0][2]} °F"
    )

@app.route('/api/v1.0/<start>/<end>')
def date_start_end(start, end):

    session = Session(engine)

    query_date_start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    query_date_end = dt.datetime.strptime(end, '%Y-%m-%d').date()

    temp_list = [func.min(measurement.tobs),
                func.max(measurement.tobs),
                func.avg(measurement.tobs)]
    
    date_temp = session.query(*temp_list).\
                filter(func.strftime('%Y-%m-%d', measurement.date) >= query_date_start).\
                filter(func.strftime('%Y-%m-%d', measurement.date) <= query_date_end).all()

    session.close()


    return (
        f"Analysis of temperature from {start} to {end}:<br/>"
        f"Minimum temperature: {date_temp[0][0]} °F<br/>"
        f"Maximum temperature: {date_temp[0][1]} °F<br/>"
        f"Average temperature: {date_temp[0][2]} °F"
    )


if __name__ == '__main__':
    app.run(debug=True)
