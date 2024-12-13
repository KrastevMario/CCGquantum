from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True)

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            card_id INTEGER,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER,
            player2_id INTEGER,
            winner_id INTEGER,
            match_date TEXT,
            FOREIGN KEY (player1_id) REFERENCES players (id),
            FOREIGN KEY (player2_id) REFERENCES players (id),
            FOREIGN KEY (winner_id) REFERENCES players (id)
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
        room = data.get('room', None)
    if room:
        emit('game_update', data, room=room)  # Send update to specific room
    else:
        emit('error', {'msg': 'No room specified for the move.'})

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"Player joined room {room}"}, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data['room']
    leave_room(room)
    emit('message', {'msg': f"Player left room {room}"}, room=room)

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000)
