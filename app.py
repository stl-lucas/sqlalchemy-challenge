import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; and /api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data"""
    # Query all precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station data"""
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        all_stations.append(stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate start date 12 months prior to last record date
    last_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_12 = (dt.datetime.strptime(last_date.date, '%Y-%m-%d') - timedelta(days=365)).strftime("%Y-%m-%d")

    """Return a list of all tobs data for highest activity station last 12 months"""
    # Query all tobs
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date > last_12).all()

    session.close()

    # Create a dictionary from the row data and append to a list of tobs
    all_tobs = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start_summary(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all summary data starting at the start date"""
    # Query summary stats from start date
    results = session.query(func.min(Measurement.prcp), func.max(Measurement.prcp), func.avg(Measurement.prcp)).filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary from the row data and append the summary data
    summary_start = []
    for min_prcp, max_prcp, avg_prcp in results:
        summary_dict = {}
        summary_dict["min"] = min_prcp
        summary_dict["max"] = max_prcp
        summary_dict["avg"] = avg_prcp
        summary_start.append(summary_dict)

    return jsonify(summary_start)

@app.route("/api/v1.0/<start>/<end>")
def end_summary(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all summary data starting at the start date through the end date"""
    # Query summary stats from start date to end date
    results = session.query(func.min(Measurement.prcp), func.max(Measurement.prcp), func.avg(Measurement.prcp)).filter(Measurement.date > start).filter(Measurement.date < end).all()

    session.close()

    # Create a dictionary from the row data and append the summary data
    summary_dates = []
    for min_prcp, max_prcp, avg_prcp in results:
        summary_dict = {}
        summary_dict["min"] = min_prcp
        summary_dict["max"] = max_prcp
        summary_dict["avg"] = avg_prcp
        summary_dates.append(summary_dict)

    return jsonify(summary_dates)


if __name__ == '__main__':
    app.run(debug=True)
