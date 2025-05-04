from flask import Flask
import pytest


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True

    with app.test_request_context():
        yield app
