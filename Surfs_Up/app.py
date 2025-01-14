# Importing the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
from flask import Flask, jsonify
import datetime as dt
#################################################
# Database Setup
#################################################

# Creating engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declaring a Base using `automap_base()`
Base = automap_base()
# Reflecting the database tables using the base class
Base.prepare(autoload_with = engine)

# Assigning the classes `measurement` and `station` to a variable called `Measurement`
# and `Station` respectively
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creating a session
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# route for the home page 
"""Note for the user and List all available api routes."""
@app.route("/")
def welcome():
    return (
        f"Important Note: Date format is year/month/date<br/>"
        f"For second last address add a start date after the /<br/>"
        f"For the last address add start date after the first / and end date after the second /<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def prep():
    # retrieving the recent date, converting it into string and assigning it to a variable.
    recent_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    # converting the previous date in string into datetime format.
    reccent_date = datetime.strptime(recent_date_str, '%Y-%m-%d')

    # calculating the date one year before the recent date.
    past_year_date = reccent_date-dt.timedelta(days = 365 )

    # extracting the date and precipitation value from the past year and closing the session.
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= past_year_date).all()
    session.close()

    # converting the data extracted into a dictionary
    data_dict = [{row.date : row.prcp} for row in data]

    return jsonify(data_dict)

@app.route("/api/v1.0/stations")
def station():
    # query to get the station data.
    station_data = session.query(Station.station).all()

    # converting the data into list
    station_list = list(np.ravel(station_data))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temp():
    # a query to get date and tobs for the past year for the most active station
    data_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == 'USC00519281').all()
    
    # converting the data into list.
    data_temp_list = list(np.ravel([temp[1] for temp in data_temp]))

    return jsonify(data_temp_list)

""" used try and except for the wrong inputs from the users in the following routes"""
@app.route("/api/v1.0/<start>")
def temp_stat (start):
    try:
    # converting the user given date into datetime format.
        str_date = datetime.strptime(start, '%Y-%m-%d')

    # a query to get the min, avg, max temperature for the data from the start date given
        data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= str_date).all()
    
    # converting the data into a dictionary.
        data_dict = [{"Minimum Temp":row[0], "Average Temp":row[1], "Maximum Temp":row[2]} for row in data]

        return jsonify(data_dict)
    except:
        return(
               f"Error <br/>"
               f"You might have miss spelled or mistaken in the date format<br/>"
               f"Please see exact address or the format of the date to be given on the homepage."
               )


@app.route("/api/v1.0/<start>/<end>")
def temp_stat_start_end(start, end):
    try:
    # converting the start and end date from user into datetime format.
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')

    # a query to get the min, avg, max temperature for the data in between the start date and the end date given.
        data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # converting the data into a dictionary.
        data_dict = [{"Minimum Temp":row[0], "Average Temp":row[1], "Maximum Temp":row[2]} for row in data]
        return jsonify(data_dict)
    except:
           return(
               f"Error <br/>"
               f"You might have miss spelled or mistaken in the date format<br/>"
               f"Please see exact address or the format of the date to be given on the homepage."
               )
    
if __name__ == '__main__':
    app.run(debug=True)