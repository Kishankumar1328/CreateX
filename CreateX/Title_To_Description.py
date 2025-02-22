from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import time

app = Flask(__name__)

# Initialize the text generation model
generator = pipeline("text2text-generation", model="google/flan-t5-large")

@app.route('/')
def home():
    return render_template('title_to_description.html')

@app.route('/generate', methods=['POST'])
def generate_description():
    try:
        data = request.get_json()
        title = data.get('title', '')
        max_length = int(data.get('maxLength', 250))
        temperature = float(data.get('temperature', 0.7))

        if not title:
            return jsonify({'error': 'Please enter a title'}), 400

        # Add delay to show loading animation (optional)
        time.sleep(1)

        # Generate description
        input_text = f"Generate a detailed and engaging description for: {title}"
        result = generator(
            input_text,
            max_length=max_length,
            do_sample=True,
            temperature=temperature
        )[0]['generated_text']

        return jsonify({
            'success': True,
            'description': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)