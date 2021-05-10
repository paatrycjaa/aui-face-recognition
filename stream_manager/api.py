from flask import Flask
from flask_restx import Resource, Api

from stream_manager import StreamManager

app = Flask(__name__)
api = Api(app)
stream_manager = StreamManager()


@api.route('/streams')
class Manager(Resource):
    def get(self):
        return stream_manager.source_urls

    def post(self):
        return stream_manager.submit_stream()

if __name__ == '__main__':
    stream_manager.start()
    app.run(debug=True, port=5001)
