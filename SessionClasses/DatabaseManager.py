import json
import os

from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Default value to suppress error messaging
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # Default value to suppress error messaging
db = SQLAlchemy(app)


class TestSession(db.Model):
    """
    Table containing data about the test run that was made.
    """
    __tablename__ = 'testsession'
    id              = db.Column(db.Integer, primary_key=True, nullable=False)
    assertion_level = db.Column(db.String, nullable=False)
    start_time      = db.Column(db.String)
    end_time        = db.Column(db.String)
    total_time      = db.Column(db.Float)
    endpoint        = db.Column(db.String, nullable=False)
    username        = db.Column(db.String, nullable=True)

    def __init__(self, assertion_level, start_time, end_time, total_time, endpoint, username):
        self.assertion_level = assertion_level
        self.start_time      = start_time
        self.end_time        = end_time
        self.total_time      = total_time
        self.endpoint        = endpoint
        self.username        = username


class Tests(db.Model):
    """
    Table containing each test-file's results and info.
    """
    __tablename__ = 'tests'
    id           = db.Column(db.Integer, primary_key=True)
    session_id   = db.Column(db.Integer, db.ForeignKey('testsession.id'))
    tool_name    = db.Column(db.String)
    test_name    = db.Column(db.String)
    test_passed  = db.Column(db.Boolean)
    test_details = db.Column(db.String)
    rel_session  = db.relationship('TestSession', backref=db.backref('tests_backref'))

    def __init__(self, tool_name, test_name, test_passed, test_details):
        self.tool_name    = tool_name
        self.test_name    = test_name
        self.test_passed  = test_passed
        self.test_details = test_details


class Database:
    """
    Handles data prep and updates for the database.
    """
    def __init__(self, ts, dp):
        """
        Creates/updates a database with new session data.
        :param ts: automated test session object
        :param dp: database path from main.py
        """
        self.database_path = dp
        self.test_session = ts

        if not os.path.exists(os.sep.join(self.database_path.split(os.sep)[:-1])):
            print("Cannot find database path, skipping update: {}".format(self.database_path))
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///' + self.database_path
            db.create_all()

            # Update the session table
            session_tuple = (
                self.test_session.current_assertion_level,
                datetime.fromtimestamp(self.test_session.start_time_ms).replace(microsecond=0),
                datetime.fromtimestamp(self.test_session.end_time_ms).replace(microsecond=0),
                round((self.test_session.end_time_ms - self.test_session.start_time_ms) / 60, 2),
                self.test_session.endpoint,
                self.test_session.arg_commands['arg_0']
            )
            session_data = TestSession(*session_tuple)
            db.session.add(session_data)

            # Update the tests table
            for assert_lvl, dict1 in self.test_session.test_results.items():
                for brwsr, dict2 in dict1.items():
                    for tool_cat, tools in dict2.items():
                        for tool, test_dict in tools.items():
                            for file_name, result in test_dict.items():
                                test_tuple = (
                                    ' - '.join([tool_cat, tool]),
                                    file_name,
                                    True if result == 'PASS' else False,
                                    result
                                )
                                test_data = Tests(*test_tuple)
                                test_data.rel_session = session_data
                                db.session.add(test_data)

            db.session.commit()
            print("Database {} successfully updated!\n".format(self.database_path))
