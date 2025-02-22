from flask import Flask, render_template, request
from resemble import Resemble
import os

app = Flask(__name__)

# Resemble.ai API key
Resemble.api_key('Vhm4UepGAhMuVogwE8A6igtt')  # Replace with your actual API key

# Ensure upload and output directories exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('voice_clone.html')

@app.route('/clone', methods=['POST'])
def clone():
    if 'audio' not in request.files:
        return "No audio file uploaded", 400

    # Save the uploaded audio file
    audio_file = request.files['audio']
    audio_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(audio_path)

    # Call Resemble.ai API to clone the voice
    try:
        cloned_audio_url = create_clip_with_resemble(audio_path)
        return render_template('script_to_description.html', cloned_audio_url=cloned_audio_url)
    except Exception as e:
        return f"Error cloning voice: {str(e)}", 500

def create_clip_with_resemble(audio_path):
    # Get the default project UUID
    projects = Resemble.v2.projects.all(1, 10)
    if not projects['items']:
        raise Exception("No projects found in Resemble.ai")
    project_uuid = projects['items'][0]['uuid']

    # Get the first voice UUID
    voices = Resemble.v2.voices.all(1, 10)
    if not voices['items']:
        raise Exception("No voices found in Resemble.ai")
    voice_uuid = voices['items'][0]['uuid']

    # Create a clip using the uploaded audio
    body = "This is a test clip generated from the uploaded audio."
    response = Resemble.v2.clips.create_sync(
        project_uuid,
        voice_uuid,
        body,
        title="Cloned Voice",
        sample_rate=22050,
        output_format="wav"
    )

    if 'audio_src' not in response:
        raise Exception("Failed to create clip: " + str(response))

    return response['audio_src']

if __name__ == '__main__':
    app.run(debug=True)
