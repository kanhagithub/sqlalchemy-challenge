# Import the dependencies.
import datetime as dt
#import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
from flask import Flask, jsonify
#import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Define a function which calculates and returns the the date one year from the most recent date
def date_prev_year():
    """ date of previous year"""
    # Create the session
    session = Session(engine)

    # Define the most recent date in the Measurement dataset
    # Then use the most recent date to calculate the date one year from the last date
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar() 
    most_recent_date = dt.datetime.strptime(most_recent_date_str, '%Y-%m-%d').date()
    query_date = most_recent_date - dt.timedelta(days=365)

    # Close the session                   
    session.close()

    # Return the date
    return(query_date)
    
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2015-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve only the last 12 months of data"""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all passengers
    query_scores = session.query(Measurement.date, Measurement.prcp). filter(Measurement.date >= date_prev_year()).all()

    session.close()

     # Create a dictionary from the row data and append to a list of prcp_list
    prcp_list = []
    for date, prcp in query_scores:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

# Return a list of jsonified precipitation data for the previous 12 months 
    return jsonify(prcp_list)

# Define what to do when the user hits the station URL
@app.route("/api/v1.0/stations")
def stations():
    """Returns jsonified data of all of the stations in the database"""
    # Create the session
    session = Session(engine)

 # Query all stations
    results = session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
     # Create a dictionary from the row data and append to a list of all_station
    all_station=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        all_station.append(station_dict)
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year"""
    # Create our session
    session = Session(engine)

    # Query tobs data from last 12 months from the most recent date from Measurement table
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= date_prev_year()).all()

    # Close the session                   
    session.close()

    # Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    """TMIN, TAVG, and TMAX for a list of dates"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #start='2016-08-23'
    # Make a list to query (the minimum, average and maximum temperature)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Query the data from start date to the most recent date
    start_data = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()

        # Extract the temperature statistics from the query results
    min_temp, max_temp, avg_temp = start_data[0]

    # Return the results as JSON
    return jsonify({
        'start_date': start,
        'min_temperature': min_temp,
        'max_temperature': max_temp,
        'avg_temperature': avg_temp
    })


    
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    # Extract the temperature statistics from the query results
    min_temp, max_temp, avg_temp = results[0]

    # Return the results as JSON
    return jsonify({
        'start_date': start,
        'end_date': end,
        'min_temperature': min_temp,
        'max_temperature': max_temp,
        'avg_temperature': avg_temp
    })

   
# Define main branch 
if __name__ == "__main__":
    app.run(debug = True)
   