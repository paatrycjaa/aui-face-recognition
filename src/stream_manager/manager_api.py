from flask import Flask, jsonify
from flask_restx import Resource, Api
import threading
import time

from stream_manager import StreamManager, make_analysed_url

app = Flask(__name__)
stream_manager = StreamManager()
api = Api(app)


@api.route('/streams')
class Manager(Resource):
    def get(self):
        # stream_manager.update_urls()
        result = stream_manager.get_stream_urls()
        return jsonify([
            {
                'source_url': source_url,
                'analyzed_url': make_analysed_url(source_url),
                'last_online': str(data['last_online']),
                'last_analysis': str(data['last_analysis']) if data['last_analysis'] is not None else None
            } for source_url, data in result.items()
        ])

    def post(self):
        return jsonify(stream_manager.submit_stream())


if __name__ == '__main__':
    stream_manager.start()
    app.run(port=5001)
