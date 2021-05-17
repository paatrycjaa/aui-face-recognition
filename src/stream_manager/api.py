from flask import Flask, jsonify
from flask_restx import Resource, Api
import threading
import time

from src.stream_manager.stream_manager import StreamManager

app = Flask(__name__)
stream_manager = StreamManager()
api = Api(app)


@api.route('/streams')
class Manager(Resource):
    def get(self):
        result = stream_manager.get_stream_urls()
        return jsonify(result)

    def post(self):
        return jsonify(stream_manager.submit_stream())


if __name__ == '__main__':
    stream_manager.start()
    app.run(port=5001)
