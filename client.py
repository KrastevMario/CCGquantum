import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import socketio
import os

# Get server address from environment variable or default
SERVER_URL = os.getenv('SERVER_URL', 'http://127.0.0.1:5000')

# Connect to the server
sio = socketio.Client()

class GameApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.message_label = Label(text='Welcome to the game!')
        self.layout.add_widget(self.message_label)

        self.username_input = TextInput(hint_text='Enter your username')
        self.layout.add_widget(self.username_input)

        self.register_button = Button(text='Register')
        self.register_button.bind(on_press=self.register)
        self.layout.add_widget(self.register_button)

        self.start_game_button = Button(text='Start Game', disabled=True)
        self.start_game_button.bind(on_press=self.start_game)
        self.layout.add_widget(self.start_game_button)

        return self.layout

    def register(self, instance):
        username = self.username_input.text
        if username:
            sio.emit('register', {'username': username})
        else:
            self.message_label.text = 'Username cannot be empty.'

    def start_game(self, instance):
        sio.emit('move', {'player': self.username_input.text, 'action': 'started the game'})
        self.message_label.text = 'Game started!'

    def on_connect(self):
        self.message_label.text = 'Connected to server.'

    def on_message(self, data):
        self.message_label.text = data['msg']

    def on_register_response(self, data):
        if data['status'] == 'success':
            self.message_label.text = data['msg']
            self.start_game_button.disabled = False
        else:
            self.message_label.text = data['msg']

    def on_game_update(self, data):
        self.message_label.text = f"{data['player']} {data['action']}"

    def on_start(self):
        try:
            sio.connect(SERVER_URL)  # Connect to the server
            sio.on('message', self.on_message)
            sio.on('register_response', self.on_register_response)
            sio.on('game_update', self.on_game_update)
        except Exception as e:
            self.message_label.text = f"Failed to connect to server: {e}"

if __name__ == '__main__':
    GameApp().run()
