#Import flask and jsonify to run the api
from flask import Flask,jsonify

#Import engine to connect to sqlite and func for session operations
from sqlalchemy import create_engine,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

#Create engine to database hawaii.sqlite, reflect data to Base variable
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
#Define classes to reference in queries
Measurement=Base.classes.measurement
Station=Base.classes.station

#Define app to run api using Flask
app = Flask(__name__)

#Function define to query database to return most recent date and substract 1 year. Set it up as function for use in different API apps
def oneyearago():
    sessionfunc=Session(bind=engine)                                            #create session for function query
    recent=sessionfunc.query(func.max(Measurement.date)).scalar()               #query Measurement table for maximum value in date column, save in recent
    recent=dt.datetime.strptime(recent,"%Y-%m-%d")                              #convert string to datatime object for operations
    oneyearbefore=recent.replace(year=recent.year-1).strftime("%Y-%m-%d")       #replace year for year-1 and reconvert to string
    sessionfunc.close()                                                         #close session for function
    return oneyearbefore

#Main page, links <a> work if port 127.0.1:5000 is used by Flask
@app.route("/")
def home():
    return '<b style="color:royalblue"><span>Available static routes:</span></b></br>\
            <a href="http://127.0.0.1:5000/api/v1.0/precipitation">/api/v1.0/precipitation</a></br>\
            <a href="http://127.0.0.1:5000/api/v1.0/stations">/api/v1.0/stations</a></br>\
            <a href="http://127.0.0.1:5000/api/v1.0/tobs">/api/v1.0/tobs</a></br></br>\
            <b style="color:royalblue">Available dynamic routes:</b></br>\
            <i>Use date format:YYYY-MM-DD</i></br>\
            /api/v1.0/&lt;start&gt;</br>---DEMO: <i>(<a href="http://127.0.0.1:5000/api/v1.0/2012-01-01">Click here</a> to try route with 2012-01-01)</i></br>\
            /api/v1.0/&lt;start&gt;/&lt;end&gt;</br>---DEMO: <i>(<a href="http://127.0.0.1:5000/api/v1.0/2012-01-01/2013-01-01">Click here</a> to try route with 2012-01-01 and 2013-01-01)</i>'

#Precipitation API app
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session for query
    session=Session(bind=engine)
    #Save query to scores variable. Filter compares to oneyearago function defined earlier
    scores=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=oneyearago()).all()
    #Close session
    session.close()
    #Create dictionary to save results
    scores_dict={}
    for line in scores:
        if type(line[1])==float:            # ignore null values
            scores_dict[line[0]]=line[1]
    #Return jsonified dictionary
    return jsonify(scores_dict)

#Stations API app
@app.route("/api/v1.0/stations")
def stations():
    #Create session for query
    session=Session(bind=engine)
    #Save query to stations variable
    stations=session.query(Station).all()
    #Close session
    session.close()
    #Create dictionary to save results
    stations_dict={}
    for record in stations:
        stations_dict[record.station]={"name":record.name,
                                "latitude":record.latitude,
                                "longitude":record.longitude,
                                "elevation":record.elevation
                               }
    #Return jsonified dictionary
    return jsonify(stations_dict)

#Temperatures API app
@app.route("/api/v1.0/tobs")
def tobs():
    #Create session for query
    session=Session(bind=engine)
    #Save query to most_active variable
    most_active=session.query(Measurement).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first().station
    #Use results of last query to filter stations and oneyearago() function to filter dates
    tobs=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==most_active).filter(Measurement.date>=oneyearago()).all()
    #Close session
    session.close()
    #Create dictionary to save results
    tobs_dict={}
    for line in tobs:
        tobs_dict[line[0]]=line[1]
    #Return jsonified dictionary
    return jsonify(tobs_dict)

#Dynamic route API
@app.route("/api/v1.0/<start>",defaults={"end":None})       #If user doesn't define "end" parameter, default to None value
@app.route("/api/v1.0/<start>/<end>")                       #If user defines "end" parameter, use this value
def dates(start,end):
    #Create session for query
    session=Session(bind=engine)
    #Define selector for query
    sel=[func.min(Measurement.tobs),
         func.avg(Measurement.tobs),
         func.max(Measurement.tobs),
         func.min(Measurement.date),
         func.max(Measurement.date)]
    #Query without "end" parameter
    if end == None:
        (TMIN,TAVG,TMAX,DMIN,DMAX)=session.query(*sel).filter(Measurement.date>=start).one()
    #Query with "end" parameter
    else:
        (TMIN,TAVG,TMAX,DMIN,DMAX)=session.query(*sel).filter(Measurement.date>=start).filter(Measurement.date<=end).one()
    session.close()
    #Create dictionary to save results
    temp_dict={"From_date":DMIN,
               "To_date":DMAX,
               "Min_Temp":TMIN,
               "Max_Temp":TMAX,
               "Avg_Temp":TAVG}
    #Return jsonified dictionary
    return jsonify(temp_dict)
        
#Run app code
if __name__=="__main__":
    app.run(debug=True)