from flask import Flask
from flask_restx import Resource, Api, reqparse
from drawer import Drawer

app = Flask(__name__)
api = Api(app)
#
parser = reqparse.RequestParser()
parser.add_argument('url', type=str, help='stream url')
parser.add_argument('output_url', type=str, help='url where to send analyzed stream')
drawers = []


@api.route('/draw/')
class Analyze(Resource):
    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
        url = args['url']
        analyzed_url = args['output_url']
        if url in [drawer.source_url for drawer in drawers if drawer.is_alive()]:
            print("ALREADY DRAWING (APPARENTLY)")
            return True
        drawer = Drawer(url, analyzed_url)
        drawer.start_consume()
        drawers.append(drawer)
        drawer.start()
        return True


@api.route('/status/')
class Status(Resource):
    def get(self):
        return "online"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
