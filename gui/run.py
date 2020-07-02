from flask import Flask, render_template, jsonify, request
import ctranslate2

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    text_list = None
    language = request.form['langSrc'] + '-' + request.form['langTgt']
    source = request.form['source']
    source_list = source.split("\n")
    if language == "ab-ru":
        translator = ctranslate2.Translator(app.root_path + "/ctranslate_model")
        text_list = translator.translate_batch(source_list)
    elif language == "ru-ab":
        translator = ctranslate2.Translator(app.root_path + "/ctranslate_model")
        text_list = translator.translate_batch(source_list)
    for i, item in enumerate(text_list):
        text_list[i] = ' '.join(item[0]['tokens'])
    return jsonify({'target':"\n".join(text_list)})

if __name__ == '__main__':
    app.run(debug=True)
