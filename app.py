from flask import Flask, jsonify
# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

#Reflect Tables into SQLAlchemy ORM

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine, inspect


#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

# reflect the tables

Base = automap_base()
Base.prepare(autoload_with=engine)


# Save references to each table
Station = Base.classes.station
Station = Base.classes.station
# Create our session (link) from Python to the DB

Base = automap_base()
Base.prepare(autoload_with=engine)
measurement = Base.classes.measurement

Base = automap_base()
Base.prepare(autoload_with=engine)
station = Base.classes.station

session = Session(engine)

inspector = inspect(engine)
inspector.get_table_names()


# Find the most recent date in the data set.
session.query(measurement.date).order_by(measurement.date.desc()).first()


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

# Have the home page return the information of the different routes
@app.route("/")
def welcome():
    # List all routes that are available in the home page
    return (
        f"<p> Mambo Jambo Hawaii weather API!!!!!!</p>"
        f"<p>All routes available:</p>"
        f"/api/v1.0/precipitation<br/>Returns a JSON representation of percipitation data for the dates between {last_12mnth} and {last_date[0][0]}<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of the weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the Temperature Observations (tobs) for each station for the dates between {last_12mnth} and {last_date[0][0]}<br/><br/>"
        f"/api/v1.0/yourstartdate(yyyy-mm-dd)<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates from the given start date in yyyy-mm-dd format <br/><br/>."
        f"/api/v1.0/start_date(yyyy-mm-dd)/end_date(yyyy-mm-dd)<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and end date<br/><br/>."
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("precipitation status:OK")
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    lastDate = session.query(func.max(measurement.date)).first()[0]
    lastDate = dt.datetime.strptime(lastDate, '%Y-%m-%d')

    # Calculate the date 1 year ago from the last data point in the database
    prevYear = lastDate - dt.timedelta(365)

    # Perform a query to retrieve the data and precipitation scores
    result = session.query(measurement.date,measurement.prcp).filter(measurement.date>=prevYear).all()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    df = pd.DataFrame(result).set_index('date')

    # Sort the dataframe by date
    df = df.sort_index()

    # Return the JSON representation of your dictionary.
    return jsonify(prcp_totals)


@app.route("/api/v1.0/stations")
def station():
    print("station status:OK")
    # Design a query to calculate the total number of stations in the dataset
    stations = session.query(station).count()
    print(f"Stations Available: {stations} ")
    # Return a JSON list of stations from the dataset.
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    print("tobs status:OK")
    # What are the most active stations? (i.e. what stations have the most rows)?
    # List the stations and the counts in descending order.
    mostActive = session.query(measurement.station,func.count()).group_by(measurement.station)\
    .order_by(func.count().desc()).all()

    # most active station string
    mActStat = mostActive[0][0]

    print(f"The Most Active Stations:")
    mostActive

    # Finding most active station 
    mActStat = mostActive[0][0]
    print(f"The Most Active Station: {mActStat}")
    
    
    # Using the station id from the previous query, calculate the lowest temperature recorded, 
    # highest temperature recorded, and average temperature of the most active station?

    tobs = measurement.tobs
    mActStatTemp = session.query(func.min(tobs),func.max(tobs),func.avg(tobs)).\
    filter(measurement.station==mActStat).all()

    print(f"The Temperatures of the Most Active Station:")
    print(f"Low: {mActStatTemp[0][0]} High: {mActStatTemp[0][1]} Average: {round(mActStatTemp[0][2], 1)}")

    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_totals)





#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/<start>")
def start_date(start):
    print("start_date status:OK")
    # convert the tsring from user to date
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    last_date_dd = (dt.datetime.strptime(last_date[0][0], '%Y-%m-%d')).date()
    first_date_dd = (dt.datetime.strptime(first_date[0][0], '%Y-%m-%d')).date()
    # if fgiven start_date greater than last or lesser than first available date in dataset, print the following
    if start_date > last_date_dd or start_date < first_date_dd:
        return(f"Select date range between {first_date[0][0]} and {last_date[0][0]}")
    else:
        # Return a JSON list of the minimum temperature, the average temperature,
        # and the max temperature for a given start range.
        start_min_max_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                           func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
        start_date_data = list(np.ravel(start_min_max_temp))
        return jsonify(start_date_data)




@app.route("/api/v1.0/<start>/<end>")
def end_date(start, end):
    print("start and end status:OK")
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    last_date_dd = (dt.datetime.strptime(last_date[0][0], '%Y-%m-%d')).date()
    first_date_dd = (dt.datetime.strptime(first_date[0][0], '%Y-%m-%d')).date()
    if start_date > last_date_dd or start_date < first_date_dd or end_date > last_date_dd or\
            end_date < first_date_dd:
        return(f"Select date range between {first_date[0][0]} and {last_date[0][0]}")
    else:
        # Return a JSON list of the minimum temperature, the average temperature,
        # and the max temperature for a given start-end range.
        start_end_min_max_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                               func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(
                Measurement.date <= end_date).all()
        start_end_data = list(np.ravel(start_end_min_max_temp))
        return jsonify(start_end_data)



if __name__ == "__main__":
    app.run(debug=True)