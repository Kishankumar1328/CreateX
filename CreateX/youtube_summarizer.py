from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

app = Flask(__name__)

# Load summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    video_id_match = re.search(r"(?:v=|youtu.be/|embed/|/v/|/e/|watch\?v=|&v=)([a-zA-Z0-9_-]{11})", url)
    return video_id_match.group(1) if video_id_match else None


def get_transcript(video_url):
    """Fetches the transcript of a YouTube video."""
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL"
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except Exception as e:
        return f"Error: {str(e)}"


def summarize_text(text):
    """Summarizes the transcript using the Transformers summarization model."""
    try:
        if len(text) < 100:
            return text  # Skip summarization if the text is too short

        chunk_size = 500
        text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        summaries = [
            summarizer(
                chunk,
                max_length=max(50, int(len(chunk) * 0.2)),
                min_length=max(20, int(len(chunk) * 0.1)),
                do_sample=False
            )[0]["summary_text"]
            for chunk in text_chunks
        ]
        return " ".join(summaries)
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/')
def home():
    return render_template('youtube_summarizer.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        video_url = request.json.get('video_url')
        if not video_url:
            return jsonify({'error': 'Please enter a valid YouTube URL'}), 400

        transcript = get_transcript(video_url)
        if "Error" in transcript:
            return jsonify({'error': transcript}), 400

        summary = summarize_text(transcript)
        return jsonify({'transcript': transcript, 'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
