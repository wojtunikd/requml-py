from dotenv import load_dotenv
from functools import wraps
from flask import Flask, Response, request
from flask_restful import Api, Resource

from bson.json_util import dumps

from controller import getOrder, markOrderComplete, getOrderUseCases, getAllOrders, deleteAllOrders, deleteAnOrder
from authentication import getAdmin, verifyPassword, generateJWT, decodeAndVerifyJWT

from Analysis.analysis import conductFullAnalysis

load_dotenv()

app = Flask(__name__)
api = Api(app)


# Decorator implementation for JWT follows tutorial by Michael Aboagye
# https://geekflare.com/securing-flask-api-with-jwt/
def authenticateJWT(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            # The token is provided in the following format: Bearer Token
            # To obtain the token only, the string needs to be split on whitespace and the second value is selected
            tokenValues = request.headers.get("Authorization").split()

            if len(tokenValues) < 2:
                return {"message": "Please provide a valid token to proceed"}, 401

            token = tokenValues[1]

        if token is None:
            return {"message": "Please provide a valid token to proceed"}, 401

        try:
            decodeAndVerifyJWT(token)
        except Exception as error:
            print(error)
            return {"message": "The token provided is invalid. Please log in again"}, 401

        return f(*args, **kwargs)

    return decorator


def conductOrderAnalysis(order):
    analysis = conductFullAnalysis(order)
    markOrderComplete(order["_id"])

    return analysis, 200


def initiateOrder(order):
    if order is None:
        return {"message": "The order has not been found"}, 404
    elif order["completed"]:
        return {"message": "The order has already been analysed"}, 403
    else:
        return conductOrderAnalysis(order)


def rerunAnalysis(order):
    if order is None:
        return {"message": "The order has not been found"}, 404
    else:
        return conductOrderAnalysis(order)


class InitiateAnalysis(Resource):
    @authenticateJWT
    def post(self, orderId):
        return initiateOrder(getOrder(orderId))


class RerunAnalysis(Resource):
    @authenticateJWT
    def post(self, orderId):
        return rerunAnalysis(getOrder(orderId))


class OrderUseCases(Resource):
    @authenticateJWT
    def get(self, orderId):
        useCases = getOrderUseCases(orderId)

        return Response(
            dumps(useCases, indent=2),
            mimetype="application/json"
        )


class OrderDetails(Resource):
    @authenticateJWT
    def get(self, orderId):
        order = getOrder(orderId)

        if order is None:
            return {"message": "The order has not been found."}, 404

        return Response(
            dumps(order, indent=2),
            mimetype="application/json"
        )


class AllOrders(Resource):
    @authenticateJWT
    def get(self):
        orders = getAllOrders()
        return Response(
            dumps(orders, indent=2),
            mimetype="application/json"
        )


class DeleteOrder(Resource):
    @authenticateJWT
    def delete(self, orderId):
        deleted = deleteAnOrder(orderId)
        if deleted is None:
            return {"message": "The order couldn't be found and deleted."}, 404
        else:
            return {"message": "The order has been deleted successfully."}, 200


class DeleteAllOrders(Resource):
    @authenticateJWT
    def delete(self):
        deleteAllOrders()
        return {"message": "All the existing orders have been deleted successfully."}, 200


class Login(Resource):
    def post(self):
        adminAccount = getAdmin(request.json["email"])
        if verifyPassword(adminAccount["password"], request.json["password"]):
            generatedToken = generateJWT()
            return {"token": generatedToken}, 200
        else:
            return {"message": "Authentication failed"}, 401


@app.errorhandler(Exception)
def serverError(error):
    print(error)
    return {"message": "Error while processing your request. Please try again!"}, 500


api.add_resource(InitiateAnalysis, "/api/initiate/<string:orderId>")
api.add_resource(OrderUseCases, "/api/uc/<string:orderId>")
api.add_resource(RerunAnalysis, "/api/orders/rerun/<string:orderId>")
api.add_resource(DeleteOrder, "/api/orders/delete/<string:orderId>")
api.add_resource(DeleteAllOrders, "/api/orders/delete/all")
api.add_resource(OrderDetails, "/api/orders/<string:orderId>")
api.add_resource(AllOrders, "/api/orders/all")
api.add_resource(Login, "/api/login")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
