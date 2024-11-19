# Import the dependencies.i
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

# Get the last 12 months of precipitation data
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    twelve_months = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= twelve_months).order_by(Measurement.date).all()

    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)


# Retrieve stations
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)


    stations_all = Station.query.all()
    stations_list = [{'station': station.station, 'name': station.name} for station in stations_all]
    return jsonify(stations_list)

# Get the most active station (station with the most measurements in the last year)
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    twelve_months = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    twelve_months_stations = session.query(Measurement.tobs).filter(Measurement.station=='USC00519281')\
    .filter(Measurement.date>= twelve_months).all()
    
    most_active = session.query(Measurement.station,func.count(Measurement.station))\
    .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active

    if most_active:
        station_id = most_active.station
        twelve_months_stations = session.query(Measurement.tobs).filter(Measurement.station=='USC00519281')\
        .filter(Measurement.date>= twelve_months).all()

        tobs_data = [{'date': date, 'tobs': tobs} for date, tobs in twelve_months_stations]
        return jsonify(tobs_data)

#Retrieve temperature data
 
@app.route('/api/v1.0/<start>')
def start_temp_stats(start):
    session = Session(engine)

    temp = session.query(
    func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)
).filter(Measurement.station == 'USC00519281').all()
    
    temp_stats = {
        "TMIN": temp[0][0],
        "TAVG": temp[0][1],
        "TMAX": temp[0][2]
    }
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
    
session.close()
