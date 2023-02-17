########### LIBRERIE ###########

from flask import Flask, request, render_template, send_file
from google.cloud import firestore, storage
from werkzeug.utils import secure_filename
from secret import secret
import os


########### CREAZIONE APPLICAZIONE FLASK ###########

app = Flask(__name__)


########### PAGINA INIZIALE ###########

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def main():
    return render_template("home.html")


########### SALVATAGGIO DATI SU DATABASE FIRESTORE E CLOUD STORAGE ###########

@app.route('/sensors/cam', methods=['POST'])
def save_data():
    s = request.values['secret']
    if s == secret:

        name = request.values['name']
        time = request.values['time']
        db = firestore.Client()
        db.collection('cam').document(time).set({'individuo': name, 'ora': time})


        file = request.files['file']
        fname = secure_filename(file.filename)
        file.save(os.path.join('/tmp/', fname))

        client = storage.Client()
        bucket = client.bucket('raccolta-screen')
        source_file_name = fname
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(os.path.join('/tmp/', fname))


########### OUTPUT: CONVERSIONE DATI DEL DATABASE IN DIZIONARIO ###########

@app.route('/sensors/cam', methods=['GET'])
def read_all():
    db = firestore.Client()
    data = []
    for doc in db.collection('cam').stream():
        x = doc.to_dict()
        data.append([x['individuo'],  x['ora']])
    return data


########### OUTPUT: ACCESSO ALLA TABELLA DEI DATI CONVERTITI ###########

@app.route('/table', methods=['GET'])
def create_table():
    data = read_all()
    return render_template('table.html', data=data)


########### OUTPUT: ACCESSO ALLE IMMAGINI DEL CLOUD STORAGE ###########

@app.route('/photo', methods=['GET'])
def view_screen():
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('raccolta-screen')
    filename = [filename.name for filename in list(bucket.list_blobs(prefix=''))]

    im = filename[len(filename)-1]
    blob = bucket.blob(im)
    blob.download_to_filename(os.path.join('/tmp/', im))
    return send_file(os.path.join('/tmp/', im), mimetype='image/jpeg')


########### ESECUZIONE FLASK SULLA PORTA 8080 ###########

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)