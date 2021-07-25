from dotenv import load_dotenv
from flask import Flask, Response
from flask_restful import Api, Resource

from bson.json_util import dumps

from controller import getOrder, updateActorUseCases, getOrderUseCases, getAllOrders
from Analysis.use_cases import analyseForUseCases

load_dotenv()

app = Flask(__name__)
api = Api(app)


def verifyOrder(order):
    if order is None:
        return {"message": "The order has not been found"}, 404
    elif order["completed"]:
        return {"message": "The order has already been analysed"}, 403
    else:
        actorsWithUseCases = analyseForUseCases(order)
        ucUpdate = updateActorUseCases(order["_id"], actorsWithUseCases)
        return {"message": "Order initiated", "ucParam": ucUpdate["useCasesParam"]}, 200


class InitiateAnalysis(Resource):
    def post(self, orderId):
        return verifyOrder(getOrder(orderId))


class OrderUseCases(Resource):
    def get(self, orderId):
        useCases = getOrderUseCases(orderId)

        return Response(
            dumps(useCases, indent=2),
            mimetype='application/json'
        )


class OrderDetails(Resource):
    def get(self, orderId):
        order = getOrder(orderId)

        return Response(
            dumps(order, indent=2),
            mimetype='application/json'
        )


class AllOrders(Resource):
    def get(self):
        orders = getAllOrders()
        return Response(
            dumps(orders, indent=2),
            mimetype='application/json'
        )


api.add_resource(InitiateAnalysis, "/initiate/<string:orderId>")
api.add_resource(OrderUseCases, "/uc/<string:orderId>")
api.add_resource(OrderDetails, "/orders/<string:orderId>")
api.add_resource(AllOrders, "/orders/all")


if __name__ == "__main__":
    app.run(debug=True)
