import random
from flask import Flask, render_template, request, session, redirect
from functools import wraps
import pymongo
from battleship.bts import *


app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = pymongo.MongoClient('localhost', 27017)
db = client.user_login_system


def RandomShip():
    global ship_X, ship_Y, won
    ship_X = random.randint(0, len(grid))
    ship_Y = random.randint(0, len(grid))
    won = False
    print("ship_X: ", ship_X)
    print("ship_Y: ", ship_Y)

# Decorators


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap


# Routes
from user import routes


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard/')
@login_required
def dashboard():
    global grid
    global num
    ################
    #your code here#
    ################

    grid = initialiseGrid()
    RandomShip()
    user_data = db.users.find_one(session['user'])
    num = len(user_data["matches"])
    db.users.find_one_and_update(session['user'], {
        '$set': {'matches.match_'+str(num)+'.won': False}
    })
    return render_template('main.html', grid=grid)


@app.route('/calculate', methods=["POST"])
def calculate():
    global won
    data = request.form

    ################
    #your code here#
    ################
    X = data['X']
    Y = data['Y']
    if validateRow(X) and validateCol(Y):

        xy_coord = {"X": X, "Y": Y}
        # coordinates.insert_one(xy_coord)
        print(db.users.find_one_and_update(session['user'], {
            '$push': {
              'matches.match_'+str(num)+'.moves': xy_coord
              }
        }))
        won = checkResult(grid, int(X), int(Y), ship_X, ship_Y, won)

        if won:
            user_data = db.users.find_one_and_update(session['user'], {
                '$set': {'matches.match_'+str(num)+'.won': True}
            })
            cur_match = user_data['matches']['match_'+str(num)]['moves']
            return render_template('won.html', coords=list(cur_match))

    return render_template('main.html', grid=grid)


@app.route('/leaderboard/')
@login_required
def leaderboard():
    data = db.users.find()
    values = dict()
    for user in data:
        game_arr = []
        wins = 0
        for match in user['matches']:
            if user['matches'][match]['won']:
                wins+=1
                moves = len(user['matches'][match]['moves'])
                # for play in user['matches'][match]:
                game_arr.append(moves)
    #     print(game_arr)
        game_arr.sort()
        values[user['name']] = {'best':game_arr[0],'wins':str(wins) , 'loss':str(len(user['matches']) - wins)}
        rankings = sorted(values.items(), key= lambda x: x[1]['best'])
    return render_template('leaderboard.html', data=rankings)
