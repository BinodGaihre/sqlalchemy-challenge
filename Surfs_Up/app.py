# Import the dependencies.
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

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with = engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(bind=engine)

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
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def prep():
    session = Session(engine)
    recent_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    reccent_date = datetime.strptime(recent_date_str, '%Y-%m-%d')
    past_year_date = reccent_date-dt.timedelta(days = 365 )
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= past_year_date).all()
    session.close()
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= past_year_date).all()
    data_dict = [{'date': row.date, 'prcp': row.prcp} for row in data]

    return jsonify(data_dict)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    station_data = session.query(Station.station).filter(Station.station == Measurement.station).\
        group_by(Station.station).order_by(func.count(Measurement.station).desc()).all()
    station_list = list(np.ravel(station_data))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temp():
    data_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == 'USC00519281').all()
    data_temp_list = list(np.ravel([temp[1] for temp in data_temp]))
    return jsonify(data_temp_list)

@app.route("/api/v1.0/<start>")
def temp_stat (start):
    str_date = datetime.strptime(start, '%Y-%m-%d')
    data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= str_date).all()
    data_list = list(np.ravel(data))
    return jsonify(data_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_stat_start_end(start, end):
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    data_list = list(np.ravel(data))
    return jsonify(data_list)

if __name__ == '__main__':
    app.run(debug=True)