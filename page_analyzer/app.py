from dotenv import load_dotenv
import os
from flask import Flask, render_template, redirect, url_for, flash


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

