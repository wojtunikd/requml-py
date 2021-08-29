# ReqUML Main GUI

This is the main GUI of the ReqUML application whose main role is to render the home page of the application with the submission form to add an order with user stories for analysis.


# Installation

Run the following command to download all the packages required to start the server. 
> pip install -r requirements.txt


# Environment variables

There environment variables are required to run the application:
> MONGODB_CONNECTION=
> 
> JWT_SECRET=


# Running the server

To run the application after downloading the packages, run the following command:
> python main.py
  

# API endpoints

Most API endpoints are protected. To access them, you need to log in by providing valid credentials to POST /api/login in order to obtain a JWT token which is a Bearer token for the Authorization header in HTTP requests to other endpoints.

> POST /api/login
> 
> {
>   "email": EMAIL,
>   "password": PASSWORD"
> }

This route is for logging in using valid credentials and obtaining the JWT token.

> GET /api/orders/all

This route is for retrieving all orders ever placed. JWT token required for Authorization.

> GET /api/orders/:orderId

This route is for retrieving a specific order by its unique ID. JWT token required for Authorization.

> DELETE /api/orders/delete/all

This route is for deleting all orders ever placed from the database. JWT token required for Authorization.

> DELETE /api/orders/delete/:orderId

This route is for deleting a specific order by its unique ID. JWT token required for Authorization.

> POST /api/initiate/:orderId

This route is for initiating the NLP analysis of a specific order by its unique ID. JWT token required for Authorization.

> POST /api/orders/rerun/:orderId

This route is for rerunning the NLP analysis of a specific order by its unique ID. JWT token required for Authorization.


# Folder structure and files

Folder *Analysis* contains files with functions required for the NLP analysis of classes and use cases, as well as for preprocessing. Files:

 1. analysis.py: the main analysis file that invokes other functions and returns the analysis results
 2. classes.py: a file with all the functions to elicit classes, attributes, methods and relationships from user stories
 3. use_cases.py: a file with all the functions to elicit use cases and actors from user stories
 4. preprocessing.py: a file with functions for text preprocessing

*Root* folder contains core Python files required to run the application. Files:

 1. .env: environment variables of the application
 2. .gitignore: contains a list of folders and files that should not be pushed to the Git repository
 3. Avowal.txt: the statement certifying that the project is my own work
 4. README: the current file
 5. authentication.py: a file with all the functions to authenticate an administrator, verify the JWT token or generate a new one
 6. controller.py: a file with all the functions that utilise a database connection to conduct CRUD operations
 7. main.py: a file which is the main entry point of the application and where the server is prompted to start running
 8. nltk.txt: a Heroku config file for NLTK download in the cloud
 9. Procfile: a Heroku config file for deployment
 10. requirements.txt: a config file with all the packages required to run the application
 11. runtime.txt: a config file with the Python version used
 12. test.py: a file with unit tests of some functions of the program

 # Deployment

 The server is deployed on Heroku and can be accessed via URL:
 > https://requml-py.herokuapp.com

 **Important**: Please note that for the purpose of the individual project, the application was deployed to a free-tier dyno. This means that the resources of the application in the cloud are currently limited, and the RAM allowance may be exceeded after a few analyses. Therefore, if the source code is available, it is better to run the application on a local machine. 

 The API can be used via Postman.

