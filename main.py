from dotenv import load_dotenv
from flask import Flask, Response
from flask_restful import Api, Resource

from bson.json_util import dumps

from controller import getOrder, updateActorUseCases, getOrderUseCases, getAllOrders, deleteAllOrders, deleteAnOrder
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


def rerunAnalysis(order):
    if order is None:
        return {"message": "The order has not been found"}, 404
    else:
        actorsWithUseCases = analyseForUseCases(order)
        ucUpdate = updateActorUseCases(order["_id"], actorsWithUseCases)
        return {"message": "Analysis has been rerun", "ucParam": ucUpdate["useCasesParam"]}, 200


class InitiateAnalysis(Resource):
    def post(self, orderId):
        return verifyOrder(getOrder(orderId))


class RerunAnalysis(Resource):
    def post(self, orderId):
        return rerunAnalysis(getOrder(orderId))


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

        if order is None:
            return {"message": "The order has not been found."}, 404

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


class DeleteOrder(Resource):
    def delete(self, orderId):
        deleted = deleteAnOrder(orderId)
        if deleted is None:
            return {"message": "The order couldn't be found and deleted."}, 404
        else:
            return {"message": "The order has been deleted successfully."}, 200


class DeleteAllOrders(Resource):
    def delete(self):
        deleteAllOrders()
        return {"message": "All the existing orders have been deleted successfully."}, 200


api.add_resource(InitiateAnalysis, "/initiate/<string:orderId>")
api.add_resource(OrderUseCases, "/uc/<string:orderId>")
api.add_resource(RerunAnalysis, "/orders/rerun/<string:orderId>")
api.add_resource(DeleteOrder, "/orders/delete/<string:orderId>")
api.add_resource(DeleteAllOrders, "/orders/delete/all")
api.add_resource(OrderDetails, "/orders/<string:orderId>")
api.add_resource(AllOrders, "/orders/all")


if __name__ == "__main__":
    app.run(debug=True)
