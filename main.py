import os
from dotenv import load_dotenv # type: ignore
load_dotenv()  # This loads .env from the current project directory

from gtts import gTTS
import google.generativeai as genai
import pygame

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from pymongo import MongoClient
from kivy.graphics import Color, Rectangle

# Load API Key from .env
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found! Check your .env file and myenv activation.")
else:
    print("✅ API key loaded successfully from .env")

# Configure Gemini
genai.configure(api_key=api_key)

# Debug model list
print("AVAILABLE MODELS →")
for m in genai.list_models():
    print(" -", m.name)


def get_ai_response(prompt):
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        print(f"AI Error: {e}")
        return "Error: Unable to process your request at this time."
# Function to convert text to speech and play it
def text_to_speech(text):
    try:
        tts = gTTS(text, lang='en')
        filename = "response.mp3"
        tts.save(filename)

        # Use pygame to play audio
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # Wait for audio to finish
            pass

        os.remove(filename)  # Optionally delete the file
    except Exception as e:
        print(f"Error generating or playing audio: {e}")


# MongoDB Database Connection
class Database:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["fake_news_detection_app"]  # Database name
        self.users_collection = self.db["users"]          # Collection name

    def register_user(self, username, password, role):
        try:
            if self.users_collection.find_one({"username": username}):
                print("Username already exists.")
                return False

            self.users_collection.insert_one({
                "username": username,
                "password": password,
                "role": role
            })
            return True
        except Exception as e:
            print("Error:", e)
            return False

    def validate_user(self, username, password):
        user = self.users_collection.find_one({
            "username": username,
            "password": password
        })
        return user


# Initialize database
db = Database()
class StyledLabel(Label):
    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class StyledLabel(Label):
    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Set background color to black
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


# Sign-Up Screen
class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Background Image
        background = Image(source='newspaper3.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        # Content Layout
        content_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Username Input
        self.username_input = TextInput(
            hint_text="Choose a Username",
            multiline=False,
            size_hint=(1, 0.2)
        )
        content_layout.add_widget(self.username_input)

        # Password Input
        self.password_input = TextInput(
            hint_text="Set a Password",
            multiline=False,
            password=True,
            size_hint=(1, 0.2)
        )
        content_layout.add_widget(self.password_input)

        # Role Input
        self.role_input = TextInput(
            hint_text="Enter your Role (e.g., user/admin)",
            multiline=False,
            size_hint=(1, 0.2)
        )
        content_layout.add_widget(self.role_input)

        # Sign-Up Button
        signup_button = Button(
            text="Sign Up",
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 1, 1)
        )
        signup_button.bind(on_press=self.signup_action)
        content_layout.add_widget(signup_button)

        # Back to Login Button
        back_button = Button(
            text="Back to Login",
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(1, 0.4, 0.4, 1)
        )
        back_button.bind(on_press=self.goto_login)
        content_layout.add_widget(back_button)

        layout.add_widget(content_layout)
        self.add_widget(layout)

    def signup_action(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        role = self.role_input.text

        if db.register_user(username, password, role):
            print("User registered successfully!")
            self.manager.current = 'login'
        else:
            print("Sign-Up failed! Username might already exist.")

    def goto_login(self, instance):
        self.manager.current = 'login'

# Home Screen
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Background Image
        background = Image(source='newspaper4.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        # Content Layout
        content_layout = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=20,
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        title_label = StyledLabel(
         text="Fake News Detection",
         font_size='40sp',
        bold=True,  # Bold text
         italic=True,  # Italic text
       color=(1, 0, 0, 1),  # Red text color
      halign='center',
         valign='middle',
      size_hint=(1, None),
      height=100
)
        content_layout.add_widget(title_label)

        # Login Button
        login_button = Button(
            text="Login",
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 1, 1)
        )
        login_button.bind(on_press=self.goto_login)
        content_layout.add_widget(login_button)

        # About Us Button
        about_button = Button(
            text="About Us",
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.4, 0.8, 0.4, 1)
        )
        about_button.bind(on_press=self.goto_about_us)
        content_layout.add_widget(about_button)

        # Exit Button
        exit_button = Button(
            text="Exit",
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(1, 0.4, 0.4, 1)
        )
        exit_button.bind(on_press=self.exit_app)
        content_layout.add_widget(exit_button)

        layout.add_widget(content_layout)
        self.add_widget(layout)

    def goto_login(self, instance):
        self.manager.current = 'login'

    def goto_about_us(self, instance):
        self.manager.current = 'about_us'

    def exit_app(self, instance):
        App.get_running_app().stop()
# Login Screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Background Image
        background = Image(source='newspaper3.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        # Content Layout
        content_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            size_hint=(0.8, 0.7),  # Adjust size to fit the screen better
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Username Input
        self.username_input = TextInput(
            hint_text="Enter Username",
            multiline=False,
            size_hint=(1, 0.2)
        )
        content_layout.add_widget(self.username_input)

        # Password Input
        self.password_input = TextInput(
            hint_text="Enter Password",
            multiline=False,
            password=True,
            size_hint=(1, 0.2)
        )
        content_layout.add_widget(self.password_input)

        # Button Layout (for consistent button sizes)
        button_layout = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint=(1, 0.6)
        )

        # Login Button
        login_button = Button(
            text="Login",
            size_hint=(1, 0.2),  # Consistent size
            background_normal='',
            background_color=(0.2, 0.6, 1, 1)
        )
        login_button.bind(on_press=self.login_action)
        button_layout.add_widget(login_button)

        # Sign-Up Button
        signup_button = Button(
            text="Sign Up",
            size_hint=(1, 0.2),  # Consistent size
            background_normal='',
            background_color=(0.4, 0.8, 0.4, 1)
        )
        signup_button.bind(on_press=self.goto_signup)
        button_layout.add_widget(signup_button)

        # Back to Home Button
        back_button = Button(
            text="Back to Home",
            size_hint=(1, 0.2),  # Consistent size
            background_normal='',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_button.bind(on_press=self.goto_home)
        button_layout.add_widget(back_button)

        # Add button layout to content layout
        content_layout.add_widget(button_layout)

        # Add the content layout to the main layout
        layout.add_widget(content_layout)

        # Add the main layout to the screen
        self.add_widget(layout)

    def goto_home(self, instance):
        self.manager.current = 'home'

    def login_action(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        user = db.validate_user(username, password)
        if user:
            print("Login successful!")
            self.manager.current = 'main_screen'  # Redirect to the main screen
        else:
            print("Invalid username or password")

    def goto_signup(self, instance):
        self.manager.current = 'signup'


# Main Screen
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = FloatLayout()

           # Background Image
        background = Image(source='text_layer.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        # Welcome Label
        label = Label(
            text="Welcome to the Main Screen!",
            font_size='30sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.8}
        )
        layout.add_widget(label)

        # Text Input
        self.textbox = TextInput(
            hint_text="Enter text here",
            size_hint=(0.7, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        layout.add_widget(self.textbox)

        

        # Submit Button
        submit_button = Button(
            text="Submit",
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_normal='',
            background_color=(0.2, 0.6, 1, 1)
        )
        submit_button.bind(on_press=self.submit_action)
        layout.add_widget(submit_button)

        # Go to Home Screen Button
        home_button = Button(
            text="Go to Home Screen",
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_normal='',
            background_color=(0.4, 0.8, 0.4, 1)
        )
        home_button.bind(on_press=self.goto_home)
        layout.add_widget(home_button)
# Response Label
        self.response_label = Label(
            text="",
            font_size='18sp',
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            halign="center"
        )
        layout.add_widget(self.response_label)
        self.add_widget(layout)


    def submit_action(self, instance):
        user_input = self.textbox.text

        if not user_input.strip():
            self.response_label.text = "Please enter some text."
            return

        response = get_ai_response(
            user_input +
            " The output should be true or false. If the news is not completely true or false, provide a short description (20-30 words). Even if it is false, don't throw an error and give an answer."
        )

        if "Error" in response:
            self.response_label.text = '''Your message contains content that may promote hatred,
              sexuality, racism, terrorism, or other inappropriate topics. Please ensure that your
                communication remains respectful and appropriate. 
                As a neutral AI, I am unable to respond to such content.'''
        else:
            self.response_label.text = f"AI: {response}"
            text_to_speech(response)

    def goto_home(self, instance):
        self.manager.current = 'home'




# About Us Screen
class AboutUsScreen(Screen):
    def __init__(self, **kwargs):
        super(AboutUsScreen, self).__init__(**kwargs)
        
        layout = FloatLayout()
        
        # Background Image
        background = Image(source='text_layer.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)
        
        # About Us Content
         
        about_label = Label(
    text=(
        '''
        
        
        [b]Welcome to the Fake News Detection App!

In today’s world of instant communication, the rapid spread of misinformation poses a significant challenge. 

The Fake News Detection App is here to help you navigate through this complex information landscape 
by distinguishing between factual news and potential misinformation.

Our mission is to empower individuals to make informed decisions by providing an AI-driven platform that verifies the authenticity 
of news articles, social media posts, and other online content. 
Whether you’re a concerned citizen, a journalist, or an academic, our app is designed to cater to your needs, 
ensuring you access credible and reliable information.

The app combines advanced AI algorithms, community-driven verification, and user-friendly tools to analyze news content.
 By cross-referencing trusted sources and using pattern recognition, it evaluates the likelihood of news being genuine or fake. 
 Additionally, the app provides concise explanations, helping you understand why certain content may not be entirely accurate.

We aim to promote responsible information sharing and foster a culture of media literacy. 
Together, we can combat the spread of false information and create a healthier, more trustworthy digital space.

Features Include:
	•	AI-Powered Analysis: Quick detection of false or misleading news.
	•	Text-to-Speech Integration: Listen to AI-generated insights for better accessibility.
	•	Secure Login System: Personalized experiences for users and admins.
	•	Community Feedback: Collaborative insights from users worldwide.
	•	Dynamic Design: Easy-to-use interface with visually appealing layouts.

At its core, this app is a step toward combating misinformation and fostering accountability in the digital age. 
Join us in building a community where truth prevails over falsehood. 
Together, we can ensure that everyone has the tools they need to discern fact from fiction.

Version: 1.0.0
Let’s detect, educate, and empower![/b]'''
    ),
    font_size='18sp',
    halign='center',
    valign='middle',
    markup=True,  # Enables markup for bold text
    color=(0, 0, 0, 1),  # Black color in RGBA
    size_hint=(0.8, 0.8),
    pos_hint={'center_x': 0.5, 'center_y': 0.6},
)
        layout.add_widget(about_label)
        
        # Back Button
        back_button = Button(
            text="Back to Home",
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            background_normal='',
            background_color=(0.4, 0.6, 1, 1)
        )
        back_button.bind(on_press=self.goto_home)
        layout.add_widget(back_button)
        
        self.add_widget(layout)

    def goto_home(self, instance):
        self.manager.current = 'home'


# Main App
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))  # Default screen
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(AboutUsScreen(name='about_us'))
        sm.add_widget(SignupScreen(name='signup'))
        return sm
# Run the app
if __name__ == '__main__':
    MyApp().run()