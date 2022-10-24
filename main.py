import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from payment_order import modify_xml


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './upload/'
app.config['SECRET_KEY'] = 'yada taijanai'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        snum = request.form['snum']
        purpose = request.form['purpose']
        filename = secure_filename(file.filename)
        upload_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_file)
        print(upload_file)
        modify_xml(upload_file, snum, purpose)
        return render_template('download.html')
    else:
        return render_template('index.html')


@app.route('/download.html')
def download():
    return render_template('download.html')


@app.route('/return/')
def return_files():
    try:
        return send_file('./out/download.zip', download_name='download.zip')
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
