from flask import Flask, request, render_template, jsonify
from llm_client import LLMClient
import os

app = Flask(__name__)
llm_client = LLMClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt', '')
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400
    
    result = llm_client.generate_code(prompt)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True) 