from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Database setup
def init_db():
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            score INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return "Game server is running."

@socketio.on('connect')
def handle_connect():
    emit('message', {'msg': 'Welcome to the game server!'})

@socketio.on('register')
def register(data):
    username = data['username']
    try:
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO players (username) VALUES (?)', (username,))
        conn.commit()
        conn.close()
        emit('register_response', {'status': 'success', 'msg': 'User registered!'})
    except sqlite3.IntegrityError:
        emit('register_response', {'status': 'error', 'msg': 'Username already exists.'})

@socketio.on('move')
def handle_move(data):
    emit('game_update', data, broadcast=True)  # Broadcast the move to all connected clients

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000)
