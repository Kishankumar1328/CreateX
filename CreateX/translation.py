from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Available languages in Deep Translator
LANGUAGE_CODES = GoogleTranslator().get_supported_languages()

@app.route('/')
def home():
    return render_template('translator.html', languages=sorted(LANGUAGE_CODES))

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text', '').strip()
        target_language = data.get('target_language', '').strip().lower()

        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400
        if not target_language or target_language not in LANGUAGE_CODES:
            return jsonify({"error": f"Invalid target language: {target_language}"}), 400

        # Translate using Deep Translator
        translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)

        return jsonify({
            "translated_text": translated_text,
            "source_language": GoogleTranslator().detect(text)
        })
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)