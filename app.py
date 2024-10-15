from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
INPUT_FOLDER = 'input/'
SEPARATED_FOLDER = 'separated/'

# Do input and output directories exist
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(SEPARATED_FOLDER, exist_ok=True)

app.config['INPUT_FOLDER'] = INPUT_FOLDER
app.config['SEPARATED_FOLDER'] = SEPARATED_FOLDER

# Start page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        file_path = os.path.join(app.config['INPUT_FOLDER'], file.filename)
        file.save(file_path)

        # Call your MP3/WAV processing function here (e.g., separate_mp3(file_path))
        # processed_files = separate_mp3(file_path)

        # For simplicity, redirect to a dummy result page
        return redirect(url_for('result', filename=file.filename))

# Results page
@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
