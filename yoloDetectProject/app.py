from flask import Flask, request, send_file
import os

from service import AnalyseImage, AnalyseVideo

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def GetFromModel(file, output_filename, fileType):
    if fileType == 'image':
        return AnalyseImage(file)
    elif fileType == 'video':
        return AnalyseVideo(file)
    else:
        raise Exception("Invalid file type")


@app.route('/ananlyse', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    outputFilename = request.form.get('output_filename')
    fileType = request.form.get('file_type')
    if file.filename == '':
        return 'No selected file', 400
    if file:
        file_or_path = GetFromModel(file, outputFilename, fileType)
        return send_file(file_or_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=8180)
