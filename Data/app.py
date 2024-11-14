# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Data/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all daily precipitation"""
    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

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

    """Return a list of all stations available"""
    # Query all stations
    results = session.query(Station.name, Station.station).all()

    session.close()

    all_stations = []
    for name, station in results:
        stations_dict = {}
        stations_dict["name"] = name
        stations_dict["station"] = station
        all_stations.append(stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations (tobs) for the most active station for the past year"""
    # Identify the most recent date in the dataset for the most active station
    latest_date = session.query(func.max(Measurement.date)).filter(Measurement.station == 'USC00519281').scalar()
    # Calculate the date one year ago from the latest date
    one_year_ago = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the temperature observations for the most active station for the latest year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= one_year_ago).all()

    session.close()

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return TMIN, TAVG, TMAX for all dates greater than or equal to the start date"""
    # Query to calculate TMIN, TAVG, TMAX
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary to hold the results
    temps = []
    for TMIN, TAVG, TMAX in results:
        temp_dict = {}
        temp_dict["TMIN"] = TMIN
        temp_dict["TAVG"] = TAVG
        temp_dict["TMAX"] = TMAX
        temps.append(temp_dict)

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return TMIN, TAVG, TMAX for dates between the start and end date inclusive"""
    # Query to calculate TMIN, TAVG, TMAX
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Store results in dictionary
    temps = []
    for TMIN, TAVG, TMAX in results:
        temp_dict = {}
        temp_dict["TMIN"] = TMIN
        temp_dict["TAVG"] = TAVG
        temp_dict["TMAX"] = TMAX
        temps.append(temp_dict)

    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
