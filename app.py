from flask import Flask
from flask_restful import Resource, Api
from O365 import Schedule
from datetime import datetime
import os
import time

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class OfficeCalendarStatus(Resource):
    def get(self):
        # query for all calendar events 24 hrs before and after "now"
        office_email = os.environ["OFFICE_USER"]
        office_pw = os.environ["OFFICE_PASSWORD"]
        time_string = '%Y-%m-%dT%H:%M:%SZ'
        start_time = time.strftime(time_string, time.gmtime(time.time() - (60 * 60 * 24)))
        end_time = time.strftime(time_string, time.gmtime(time.time() + (60 * 60 * 24)))
        schedule = Schedule((office_email, office_pw))
        try:
            schedule.getCalendars()
        except:
            return False
        for cal in schedule.calendars:
            try:
                result = cal.getEvents(start=start_time, end=end_time)
            except:
                return False
            for event in cal.events:
                event_json = event.toJson()
                if event_json["ShowAs"] == "Busy":
                    start = datetime.strptime(event_json["Start"], "%Y-%m-%dT%H:%M:%SZ")
                    end = datetime.strptime(event_json["End"], "%Y-%m-%dT%H:%M:%SZ")
                    if start < datetime.utcnow() < end:
                        return True
        return False


api.add_resource(HelloWorld, '/')
api.add_resource(OfficeCalendarStatus, '/api/calendarStatus')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
