from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api, Resource

from controller import getOrder, updateActorUseCases, getOrderUseCases
from Analysis.use_cases import analyseForUseCases

load_dotenv()

app = Flask(__name__)
api = Api(app)


def verifyOrder(order):
    if order is None:
        return {"message": "The order does not exist"}, 404
    elif order["completed"]:
        actorsWithUseCases = analyseForUseCases(order)
        updateActorUseCases(order["_id"], actorsWithUseCases)
    else:
        actorsWithUseCases = analyseForUseCases(order)
        updateActorUseCases(order["_id"], actorsWithUseCases)
        return {"message": "Order initiated"}, 200


class InitiateAnalysis(Resource):
    def get(self, orderId):
        return verifyOrder(getOrder(orderId))


class OrderUseCases(Resource):
    def get(self, orderId):
        return getOrderUseCases(orderId)


class OrderDetails(Resource):
    def get(self, orderId):
        order = getOrder(orderId)
        ucParam = None

        try:
            ucParam = order["ucParam"]
        except KeyError:
            print("No use case diagram parameters available.")

        return {"_id": orderId, "email": order["email"], "completed": order["completed"], "ucParam": ucParam}


api.add_resource(InitiateAnalysis, "/initiate/<string:orderId>")
api.add_resource(OrderUseCases, "/uc/<string:orderId>")
api.add_resource(OrderDetails, "/order/<string:orderId>")


if __name__ == "__main__":
    app.run(debug=True)
