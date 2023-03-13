from flask import Flask,jsonify
from sqlalchemy import create_engine,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

#Create engine to database hawaii.sqlite, reflect data to Base variable, start session for queries
app = Flask(__name__)
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement=Base.classes.measurement
Station=Base.classes.station

#Defines 
def oneyearago():
    session=Session(bind=engine)
    recent_date=session.query(Measurement).order_by(Measurement.date.desc()).first()
    recent_date=dt.datetime.strptime(recent_date.date,"%Y-%m-%d")
    oneyearbefore=recent_date.replace(year=recent_date.year-1)
    oyb_year=oneyearbefore.strftime("%Y-%m-%d")
    return oyb_year

@app.route("/")
def home():
    print("Hi")
    return "Available routes:</br>\
            /api/v1.0/precipitation</br>\
            /api/v1.0/stations</br>\
            /api/v1.0/tobs</br>\
            /api/v1.0/&lt;start&gt; or\
            /&lt;start&gt;/&lt;end&gt;"

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(bind=engine)
    scores=session.query(Measurement.date,func.sum(Measurement.prcp)).group_by(Measurement.date).filter(Measurement.date>=oneyearago()).all()
    session.close()
    scores_dict={}
    for line in scores:
        scores_dict[line[0]]=line[1]
    return jsonify(scores_dict)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(bind=engine)
    stations=session.query(Station).all()
    session.close()
    stations_dict={}
    for record in stations:
        stations_dict[record.station]={"name":record.name,
                                "latitude":record.latitude,
                                "longitude":record.longitude,
                                "elevation":record.elevation
                               }
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(bind=engine)
    mostactive=session.query(Measurement).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first().station
    tobs=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==mostactive).filter(Measurement.date>oneyearago()).all()
    session.close()
    tobs_dict={}
    for line in tobs:
        tobs_dict[line[0]]=line[1]
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def dates(start,end=0):
    session=Session(bind=engine)
    sel=[func.min(Measurement.tobs),
         func.avg(Measurement.tobs),
         func.max(Measurement.tobs),
         func.min(Measurement.date),
         func.max(Measurement.date)]
    if end == 0:
        (TMIN,TAVG,TMAX,DMIN,DMAX)=session.query(*sel).filter(Measurement.date>=start).one()
    else:
        (TMIN,TAVG,TMAX,DMIN,DMAX)=session.query(*sel).filter(Measurement.date>=start).filter(Measurement.date<=end).one()
    session.close()
    temp_dict={"From_date":DMIN,
               "To_date":DMAX,
               "Min_Temp":TMIN,
               "Max_Temp":TMAX,
               "Avg_Temp":TAVG}
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def dates_end(start,end):
    return dates(start,end)
        

if __name__=="__main__":
    app.run(debug=True)