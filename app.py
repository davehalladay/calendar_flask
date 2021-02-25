import os
import time
from datetime import datetime

import pytz
from O365 import Account
from O365.calendar import EventShowAs
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# account.authenticate(scopes=['basic', 'https://graph.microsoft.com/Calendars.Read'])


class OfficeCalendarStatus(Resource):
    def get(self):
        time_string = '%Y-%m-%dT%H:%M:%SZ'
        response = {
            "name": "Binary sensor",
            "state": {
                "open": "false",
                "timestamp": datetime.strftime(datetime.utcnow(), time_string)
            }
        }
        credentials = (os.environ["APPLICATION_ID"], os.environ["APPLICATION_SECRET"])
        start_time = time.strftime(time_string, time.gmtime(time.time() - (60 * 60 * 24)))
        end_time = time.strftime(time_string, time.gmtime(time.time() + (60 * 60 * 24)))
        try:
            account = Account(credentials)
            schedule = account.schedule()
            calendar = schedule.get_default_calendar()
            q = calendar.new_query('start').greater_equal(start_time)
            q.chain().on_attribute('end').less_equal(end_time)
            events = calendar.get_events(query=q)
            for event in events:
                if event.show_as == EventShowAs.Busy and event.start < datetime.now(tz=pytz.utc) < event.end:
                    response["state"]["open"] = "true"
                    return response
        except Exception as e:
            app.logger.error(e)
            return response
        return response


api.add_resource(OfficeCalendarStatus, '/api/calendarStatus')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
