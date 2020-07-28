from flask import Flask, render_template, jsonify, request
import util.process as process

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    tgt_list = None
    language = request.form['langSrc'] + '-' + request.form['langTgt']
    source = request.form['source']
    src_list = source.split("\n")
    sp_path_src = app.root_path +"/util/src.model"
    sp_path_tgt = app.root_path +"/util/tgt.model"
    ct_path = app.root_path + "/ctranslate_model"
    if language == "ab-ru":
        tgt_list = process.translate(src_list,sp_path_src,sp_path_tgt,ct_path)
    elif language == "ru-ab":
        tgt_list = process.translate(src_list,sp_path_src,sp_path_tgt,ct_path)
    return jsonify({'target':"\n".join(tgt_list)})

if __name__ == '__main__':
    app.run(debug=True)
