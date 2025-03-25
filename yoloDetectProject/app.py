import uuid
from io import BytesIO

import cv2
import numpy as np
from flask import Flask, request, send_file
import os

from service import AnalyseImage, AnalyseVideo

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


def GetFromModel(filePath, output_filename, fileType):
    if fileType == 'image':
        return AnalyseImage(filePath, OUTPUT_FOLDER, output_filename)
    elif fileType == 'video':
        return AnalyseVideo(filePath, OUTPUT_FOLDER, output_filename)
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
        if fileType == 'image':
            fileSuffix = request.form.get('suffix')
            uid = str(uuid.uuid4())
            filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{uid}.{fileSuffix}")
            file.save(filename)
            file_or_path = AnalyseImage(filename, OUTPUT_FOLDER, fileSuffix, uid)
            return send_file(file_or_path, as_attachment=True)
        else:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            file_or_path = AnalyseVideo(filename, OUTPUT_FOLDER, outputFilename)
            return send_file(file_or_path, as_attachment=True)


if __name__ == '__main__':
    app.run(port=8180)
