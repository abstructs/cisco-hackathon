import flask

app = flask.Flask(__name__)

@app.route('/webex', methods=['POST',])
def index():
    print(flask.request.get_data().decode('utf-8'))
    return '', 204


if __name__ == '__main__':
    import githealthbot
    app = githealthbot.create_app()
    app.run(host='0.0.0.0', port=12345)
