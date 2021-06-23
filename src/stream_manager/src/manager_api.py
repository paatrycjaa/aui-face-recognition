from flask import Flask, jsonify
from flask_restx import Resource, Api
import sys
from stream_manager import StreamManager, make_analysed_url
import json

app = Flask(__name__)
stream_manager = StreamManager()
with open('config.json') as f:
    config = json.load(f)
    stream_manager.rtmp_url = config['rtmp_url']

api = Api(app)


@api.route('/streams')
class Manager(Resource):
    def get(self):
        # stream_manager.update_urls()
        result = stream_manager.get_handlers()
        return jsonify(result)

    def post(self):
        return jsonify(stream_manager.submit_stream())


@api.route('/status/')
class Status(Resource):
    def get(self):
        return "online"


@api.route('/heartbeat/<url>')
class Heartbeat(Resource):
    def post(self, url):
        stream_manager.heartbeat_analysis(url)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        stream_manager.rtmp_url = sys.argv[1]
    if len(sys.argv) > 2:
        stream_manager.analyzer_url = sys.argv[2]
    if len(sys.argv) > 3:
        stream_manager.manager_url = sys.argv[3]
    if len(sys.argv) > 4:
        stream_manager.analysis_config['opencv'] = bool(sys.argv[4])
    if len(sys.argv) > 5:
        stream_manager.analysis_config['identification'] = bool(sys.argv[5])
    if len(sys.argv) > 6:
        stream_manager.analysis_config['scaleFactor'] = float(sys.argv[6])
    if len(sys.argv) > 7:
        stream_manager.analysis_config['minNeighbours'] = int(sys.argv[7])
    stream_manager.start()
    app.run(host='0.0.0.0', port=5001)
