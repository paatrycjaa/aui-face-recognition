from flask import Flask, jsonify
from flask_restx import Resource, Api
import sys
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


@api.route('/status/')
class Status(Resource):
    def get(self):
        return "online"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        stream_manager.rtmp_url = sys.argv[1]
    if len(sys.argv) > 2:
        stream_manager.analyzer_url = sys.argv[2]
    stream_manager.start()
    app.run(host='0.0.0.0', port=5001)
