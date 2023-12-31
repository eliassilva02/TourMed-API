from flask import jsonify, Flask, render_template, request, abort
from flask_cors import CORS
from lion import Anvisa, Pesquisa

app = Flask(__name__)

CORS(app, origins=['*'])


@app.route('/med', methods=['POST'])
def get_data():
    prod = request.json
    tipo_req = prod.get('Requisição')
    med = prod.get('Produto')

    if Anvisa(tipo_req, med) != 'A consulta não retornou nenhum resultado.':
        return Anvisa(tipo_req, med)
    else:
        return Pesquisa(med)


if __name__ == '__main__':
    app.run(debug=True)
