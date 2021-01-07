import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from werkzeug.exceptions import HTTPException
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def retrive_drinks():
    all_drinks = Drink.query.all()
    if all_drinks is None or len(all_drinks) == 0:
        abort(404)
    # print(len(all_drinks))
    drinks = [
        drink.short() for drink in all_drinks]
    # print("Drinks: ",drinks)
    return jsonify({
        'success': True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrive_drinks_details(auth):
    all_drinks = Drink.query.all()
    drinks = [
        drink.long() for drink in all_drinks]
    if drinks is None or len(drinks) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(auth):
    body = request.get_json()
    print(body)
    title_p= body.get('title', None)
    recipe_p = body.get("recipe", [])
    if type(recipe_p) != list:
        recipe_p = [recipe_p]    
    print(title_p)
    print(recipe_p)
    try:
        if title_p and recipe_p:
            drink = Drink(
                title=title_p,
                recipe=json.dumps(recipe_p))
            Drink.insert(drink)
            return jsonify({
            'success': True,
            'drinks': Drink.long(drink)
            })
        else:
            abort(404)
    except Exception as error:  
        print("\nerror => {}\n".format(error))
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(auth,id):
    body = request.get_json()
    drink = Drink.query.filter_by(id=id).first_or_404()
    try:
        drink.title = json.dumps(body.get('title', drink.title))
        recipe_p = body.get("recipe", drink.recipe)
        if type(recipe_p) != list:
            recipe_p = [recipe_p]  
        drink.recipe = json.dumps(recipe_p)
        drink.update()
        return jsonify({
                'success': True,
                'drinks': Drink.long(drink)
            })
    except Exception as error:
        print("\nerror => {}\n".format(error))
        abort(422)
        
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(auth,id):
    body = request.get_json()
    drink = Drink.query.filter_by(id=id).first_or_404()
    try:
        drink.delete()
        return jsonify({
                'success': True,
                'delete': id
            })
    except Exception as error:
        print("\nerror => {}\n".format(error))
        abort(422)


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def authentification_failed(error):
    return jsonify({
        "success": False,
        "error": AuthError,
        "message": "authentification fails"
                    }), AuthError