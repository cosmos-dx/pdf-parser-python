import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS 
import pdfplumber

app = Flask(__name__)
CORS(app) 

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'Missing file field: resume'}), 400

    file = request.files['resume']

    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type, must be PDF'}), 400

    temp_pdf_path = f'/tmp/{uuid.uuid4()}.pdf'
    file.save(temp_pdf_path)

    try:
        with pdfplumber.open(temp_pdf_path) as pdf:
            all_text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + '\n'

        resume_id = str(uuid.uuid4())

        response = {
            'message': 'Resume parsed successfully',
            'resumeId': resume_id,
            'parsedText': all_text.strip()
        }

        text_save_path = f'/tmp/resume-{resume_id}.txt'
        with open(text_save_path, 'w', encoding='utf-8') as f:
            f.write(all_text)

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

    return jsonify(response)


if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'), 
        port=int(os.getenv('PORT', '8080')),
        debug=False
    )
