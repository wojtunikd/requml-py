from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api, Resource

from controller import getOrder
from Analysis.use_cases import analyseForUseCases

load_dotenv()

app = Flask(__name__)
api = Api(app)


def verifyOrder(order):
    if order is None:
        return {"message": "The order does not exist"}, 404
    elif order["completed"]:
        return {"message": "This order has already been completed"}, 403
    else:
        analyseForUseCases(order)
        return {"message": "Order initiated"}, 200


class InitiateAnalysis(Resource):
    def get(self, orderId):
        return verifyOrder(getOrder(orderId))


api.add_resource(InitiateAnalysis, "/initiate/<string:orderId>")


if __name__ == '__main__':
    app.run(debug=True)
