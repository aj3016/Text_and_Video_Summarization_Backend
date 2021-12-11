import os
from flask import Flask, request, redirect ,render_template
from werkzeug.utils import secure_filename
import pdfplumber
import docx2txt

from utility.summarization.summarization import summarizer
from utility.question_generation.question_generation import question_answers
from utility.article_extractor.article_extractor import article_extractor
from utility.video_converter.video_converter import video_convertor

app = Flask(__name__)

app.config['UPLOAD_DOCUMENT_FOLDER'] = os.path.join(app.root_path,'static/Documents')
app.config['ALLLOWED_DOCUMENT_EXTENSIONS'] = ["DOC", "DOCX", "TXT", "PDF"]
# app.config['MAX_CONTENT_PATH'] = ''

app.config['UPLOAD_VIDEO_FOLDER'] = os.path.join(app.root_path,'static/Video/input')
app.config['READ_VIDEO_FOLDER'] = os.path.join(app.root_path,'static/Video/output')
app.config['VIDEO_MIDDLE_FOLDER'] = os.path.join(app.root_path,'static/Video/middle')
app.config['ALLLOWED_VIDEO_EXTENSIONS'] = ["MP4"]

summary = ""

@app.route('/text/input', methods=['POST'])
def take_input():
    global summary
    input = request.json['inputText']
    ratio = request.json['compression_ratio']
    summary = summarizer(input, ratio)
    return {"summary":summary}

def allowed_document(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config['ALLLOWED_DOCUMENT_EXTENSIONS']:
        return True
    else:
        return False

@app.route('/text/document', methods=['GET', 'POST'])
def take_document():
    global summary
    if request.method == "POST":
        ratio = int(request.form.get('compression_ratio')) ##convert to JSON on frontend
        if request.files:
            # name and id of field in frontend to be document
            document = request.files["document"]
            if document.filename == "":
                print("Document must have a filename")
                return redirect(request.url)
            if allowed_document(document.filename):
                filename = secure_filename(document.filename)
                document.save(os.path.join(app.config['UPLOAD_DOCUMENT_FOLDER'], filename))
                print("File Saved")

                if document.content_type == "application/pdf":
                    with pdfplumber.open(os.path.join(app.config['UPLOAD_DOCUMENT_FOLDER'], filename)) as pdf:
                        text = ""
                        for i in pdf.pages:
                            text = text + i.extract_text()
                        print(text)
                    
                    os.remove(os.path.join(app.config['UPLOAD_DOCUMENT_FOLDER'], filename))
                    print("File Deleted")

                    summary = summarizer(text, ratio)
                    return {"summary":summary}

                elif document.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text = docx2txt.process(os.path.join(app.config['UPLOAD_DOCUMENT_FOLDER'], filename))
                    print(text)

                    os.remove(os.path.join(app.config['UPLOAD_DOCUMENT_FOLDER'], filename))
                    print("File Deleted")

                    summary = summarizer(text, ratio)
                    return {"summary":summary}
                    
                elif document.content_type == "text/plain":
                    file = open(os.path.join(app.config['UPLOAD_DOCUMENT_FOLDER'], filename), "r")
                    text = file.read()
                    print(text)
                    file.close()

                    os.remove(os.path.join(app.config['UPLOAD_DOCUMENT_FOLDER'], filename))
                    print("File Deleted")

                    summary = summarizer(text, ratio)
                    return {"summary":summary}

                else:
                    print("No other extension Allowed")

            else:
                print("That file extension is not allowed")
                return redirect(request.url)
    #return render_template('upload.html')

@app.route('/text/article', methods=['POST'])
def take_article():
    global summary
    url = ratio = request.json['url']
    ratio = request.json['compression_ratio']
    text = article_extractor(url)
    print(text)
    summary = summarizer(text, ratio)
    return {"summary":summary}

def allowed_videos(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config['ALLLOWED_VIDEO_EXTENSIONS']:
        return True
    else:
        return False

@app.route('/video', methods=['GET', 'POST'])
def take_video():
    global summary
    if request.method == "POST":
        ratio = int(request.form.get('compression_ratio')) ##convert to JSON on frontend
        if request.files:
            # name and id of field in frontend to be video
            video = request.files["video"]
            if video.filename == "":
                print("Video must have a filename")
                return redirect(request.url)
            if allowed_videos(video.filename):
                filename = secure_filename(video.filename)
                video.save(os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], filename))
                print("File Saved")

                video_convertor(filename)   #takes filename

                file = open(os.path.join(app.config['READ_VIDEO_FOLDER'], 'result.txt'), "r")
                text = file.read()
                print(text)
                file.close()

                summary = summarizer(text, ratio)

                os.remove(os.path.join(app.config['READ_VIDEO_FOLDER'], 'result.txt'))
                os.remove(os.path.join(app.config['VIDEO_MIDDLE_FOLDER'], 'result.wav'))
                os.remove(os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], filename))
                print("Files Deleted")

                return {"summary":summary}

        else:
                print("That file extension is not allowed")
                return redirect(request.url)

@app.route('/quiz', methods=['GET'])
def take_summary():
    if len(summary) < 1:
        return "Please first find Summary"
    else:
        quiz_list = question_answers(summary)
        return {"quiz":quiz_list}

if __name__ == "__main__":
   app.run(debug=True)
