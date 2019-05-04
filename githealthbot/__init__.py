import flask

from githealthbot.health_model import GitHealthModel
learning_model = GitHealthModel('565323817e54c93a71359f179de54e435f9e25d2')
from githealthbot.webexapi import WebexAPI

def create_app(test_config=None):
    app = flask.Flask(__name__, instance_relative_config=True)

    webex = WebexAPI()

    @app.route('/webex', methods=['POST',])
    def index():
        postdata = flask.request.json
        webex.parse_event(postdata['data'])
        return '', 204

    return app
