from flask import Flask
from flask_restx import Resource, Api, reqparse

from analyzer import Analyzer

app = Flask(__name__)
api = Api(app)
#
parser = reqparse.RequestParser()
parser.add_argument('url', type=str, help='stream url')
analyzers = []


@api.route('/analyze/')
class Analyze(Resource):
    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
        url = args['url']
        analyzer = Analyzer(url)
        analyzers.append(analyzer)
        analyzer.start()
        return True


if __name__ == '__main__':
    app.run()
