from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
import demucs.separate
import os
import shutil
from zipfile import ZipFile
from pytubefix import YouTube
from pydub import AudioSegment

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
    cleanFolder()
    return render_template('index.html')

# Input file and process
@app.route('/input', methods=['POST'])
def upload_file():
    #if 'file' not in request.files:
    #    return redirect(request.url)
    #if file.filename == '':
    #    return redirect(request.url)
    
    vocalsOnly = "vocalsOnly" in request.form
    quality = "htdemucs"
    if ("moreQuality" in request.form):
        quality = "htdemucs_ft"
    
    youtube_url = request.form['youtube_url']
    file = request.files['file']
    file_path = ""
    fileName = ""
     
    if youtube_url:
        file_path = downloadYoutube(youtube_url)
        fileName = os.path.basename(file_path)
    
    elif file:
        file_path = os.path.join(app.config['INPUT_FOLDER'], file.filename)
        file.save(file_path)
        fileName = file.filename
        
       

    stemSplit(fileName, file_path, quality, vocalsOnly)
        
    stems = os.listdir(os.path.join(app.config['SEPARATED_FOLDER'], quality, fileName[:-4]))
    pathos = os.path.join(app.config['SEPARATED_FOLDER'], quality, fileName[:-4])
        
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
    response = send_from_directory(path[0], filename[0], as_attachment=True)

    
    return response

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
            demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", quality, file_path])
        else:
            demucs.separate.main(["--mp3", "-n", quality, file_path])
        
def cleanFolder():
    # Remove input files
    inputFiles = os.listdir(app.config['INPUT_FOLDER'])
    howManyFiles = len(inputFiles)
    if(howManyFiles >=1):
        for file in inputFiles:
            filePath = os.path.join(app.config['INPUT_FOLDER'], file)
            if(os.path.isfile(filePath)):
                try:
                    os.remove(filePath)
                    print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")
        
        # Remove separated folders
        inputFiles = os.listdir(app.config['SEPARATED_FOLDER'])
        for folder in inputFiles:
            folderPath = os.path.join(app.config['SEPARATED_FOLDER'], folder)
            folders = os.listdir(folderPath)
            for folder2 in folders:
                folderPath2 = os.path.join(folderPath, folder2)
                folders2 = os.listdir(folderPath2)
                for file in folders2:
                    filePath = os.path.join(folderPath2, file)
                    if(os.path.isfile(filePath)):
                        try:
                            os.remove(filePath)
                            print(f"Deleted: {file}")
                        except Exception as e:
                            print(f"Error deleting file {file}: {e}")

                try:
                    os.rmdir(folderPath2)
                    print(f"Deleted: {folder2}")
                except Exception as e:
                    print(f"Error deleting folder {folder2}: {e}")
                
                
                
            try:
                os.rmdir(folderPath)
                print(f"Deleted: {folder}")
            except Exception as e:
                print(f"Error deleting folder {folder}: {e}")

def downloadYoutube(url):
    video = YouTube(url).streams.filter(only_audio=True).first().download()
    base, ext = os.path.splitext(video)
    fileName = os.path.basename(base)
    new_file = os.path.join(base[:-len(fileName)], app.config["INPUT_FOLDER"], fileName ) + '.mp3'
    if os.path.isfile(new_file):
        os.remove(video)
    else:
        os.rename(video, new_file)
    
    return new_file



if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)
