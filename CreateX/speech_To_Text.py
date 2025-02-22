# app.py
from flask import Flask, render_template, jsonify, request
import speech_recognition as sr
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('speech_to_text.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return jsonify({'success': True, 'text': text})
    except sr.RequestError:
        return jsonify({'success': False, 'error': 'API unavailable'})
    except sr.UnknownValueError:
        return jsonify({'success': False, 'error': 'Could not understand audio'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)