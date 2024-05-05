from flask import Flask, request, render_template, send_file, after_this_request, redirect, url_for, flash
from pytube import YouTube
import os
import tempfile
import shutil  # Importar shutil para manejar operaciones de archivos

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    yt = YouTube(url)
    
    # Comprobar la duración del video
    max_duration = 30 * 60  # 30 minutos en segundos
    if yt.length > max_duration:
        flash("Tu video excede la duración máxima permitida de 30 minutos.", 'error')
        return redirect(url_for('index'))

    stream = yt.streams.filter(only_audio=True).first()
    temp_file, temp_path = tempfile.mkstemp(suffix='.mp4')  # pytube podría guardar inicialmente como .mp4
    os.close(temp_file)  # Cerrar el descriptor de archivo

    # Descargar el stream de audio
    stream.download(output_path=os.path.dirname(temp_path), filename=os.path.basename(temp_path))

    # Cambiar la extensión de .mp4 a .mp3
    new_path = temp_path.replace('.mp4', '.mp3')
    shutil.move(temp_path, new_path)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(new_path)
        except Exception as error:
            app.logger.error("Error removing the file:", error)
        return response

    return send_file(new_path, as_attachment=True, download_name=f"{yt.title}.mp3")

if __name__ == '__main__':
    app.run(debug=True)
