from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import demucs.separate
import os
from zipfile import ZipFile

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

# Input file and process
@app.route('/input', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        file_path = os.path.join(app.config['INPUT_FOLDER'], file.filename)
        file.save(file_path)

        quality = "htdemucs"
        vocalsOnly = True

        #stemSplit(file.filename, file_path, quality, vocalsOnly)
        
        stems = os.listdir(os.path.join(app.config['SEPARATED_FOLDER'], quality, file.filename[:-4]))
        pathos = os.path.join(app.config['SEPARATED_FOLDER'], quality, file.filename[:-4])
        
        return redirect(url_for('result', filenames=stems, path=pathos))

# Results page
@app.route('/result')
def result():
    filenames = request.args.getlist('filenames')
    pathos = request.args.getlist('path')
    return render_template('result.html', filenames=filenames, path=pathos)

# Download specific stem
@app.route('/download')
def download_file():
    filename = request.args.getlist('filename')
    path = request.args.getlist('path')
    return send_from_directory(path[0], filename[0], as_attachment=True)

# Download zipfile
@app.route('/download_zip')
def download_zip():
    paths = request.args.getlist('path')
    path = paths[0]
    zip_filenames = path.split('\\')
    zip_filename = "/" +zip_filenames[-1]+".zip"
    
    with ZipFile(path+zip_filename, 'w') as zip_object:
        stems = os.listdir(path)
        for stem in stems:
            if(stem.endswith(".mp3") or stem.endswith(".wav")):
                zip_object.write(os.path.join(path,stem), stem)
           

    return send_from_directory(path, zip_filename[1:], as_attachment=True)


def stemSplit(filename, file_path, quality, vocalsOnly):
    if(filename.endswith('.mp3')):
        if(vocalsOnly):
            demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", quality, file_path])
        else:
            demucs.separate.main(["--mp3", "-n", quality, file_path])
    else:
        if(vocalsOnly):
            demucs.separate.main(["--two-stems", "vocals", "-n", quality, file_path])
        else:
            demucs.separate.main(["-n", quality, file_path])
        


if __name__ == '__main__':
    app.run(debug=True)
