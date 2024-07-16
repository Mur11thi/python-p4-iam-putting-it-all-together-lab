#!/usr/bin/env python3

from flask import request, session,jsonify,make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

@app.before_request
def check_if_signed_in():
    if not session['user_id']:
        return {'msg':'401, Unauthorized'},401
    

class Signup(Resource):
    def post(self):
        data=request.get_json()
        existing_user = User.query.filter(User.username==data['username']).first()
        if existing_user:
            return jsonify({'msg': 'Error: Username already exists.'}), 422
        user=User(
            username= data.get('username'),
            image_url= data.get('image_url'),
            bio = data.get('bio')
        )
        user.password_hash=data.get('password')
        try:
            
            db.session.add(user)
            db.session.commit()
            session['user_id']=user.id
            return user.to_dict(),201
        except IntegrityError:
            return {'msg':'422, Unprocessable entity'},422

class CheckSession(Resource):
    def get(self):
        user =User.query.filter(User.id==session['user_id']).first()
        if user:
            return user.to_dict(),200
        else:
            return {'msg':'401, Unauthorized'},401

class Login(Resource):
    def post(self):
        username=request.get_json()['username']
        password=request.get_json()['password']
        user=User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id']=user.id
            return user.to_dict(),200
        else:
            return {'msg':'Invalid username or password'},401

class Logout(Resource):
    def delete(self):
        session['user_id']=None
        return{},204

class RecipeIndex(Resource):
    def get(self):
        recipes=[recipe.to_dict() for recipe in Recipe.query.all()]
        return recipes,200
    def post(self):
        data= request.get_json()
        title=data['title']
        instructions=data['instructions']
        minutes_to_complete=data['minutes_to_complete']
        user_id=data['user_id']
        try:
            recipe= Recipe(
            title = title,
            instructions=instructions,
            minutes_to_complete= minutes_to_complete,
            user_id= user_id
        )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(),201
        except IntegrityError:
            return {'msg':'422, Unprocessable Entity'},422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)