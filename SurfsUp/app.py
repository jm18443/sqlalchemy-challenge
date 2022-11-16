# 1. Import Flask
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True) 

Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app
app = Flask(__name__)


# 3. Define static routes
@app.route("/")
def home():
    return (
        f"Here are the routes<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

        Return the JSON representation of your dictionary."""

    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year).\
    order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    precipitate = []
    for date, prcp in results:
        precipitate_dict = {}
        precipitate_dict[date] = prcp
        precipitate.append(precipitate_dict)

    return jsonify(precipitate)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_box = list(np.ravel(results))

    return jsonify(station_box)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data.

        Return a JSON list of temperature observations for the previous year."""
    
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year).\
    order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    Observations = []
    for date, tobs in results:
        obs_dict = {}
        obs_dict[date] = tobs
        Observations.append(obs_dict)

    return jsonify(Observations)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of stations from the dataset."""
    Summation = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        sum_dict = {}
        sum_dict["Date"] = date
        sum_dict["TMIN"] = min
        sum_dict["TAVG"] = avg
        sum_dict["TMAX"] = max
        Summation.append(sum_dict)

    session.close()    

    return jsonify(Summation)


@app.route("/api/v1.0/<start>/<end>")
def end(start,end):
    """Return a JSON list of stations from the dataset."""

    session = Session(engine)

    Summation = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        sum_dict = {}
        sum_dict["Date"] = date
        sum_dict["TMIN"] = min
        sum_dict["TAVG"] = avg
        sum_dict["TMAX"] = max
        Summation.append(sum_dict)

    session.close()    

    return jsonify(Summation)


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
