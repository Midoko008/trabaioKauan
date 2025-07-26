from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Cozinheiro, Prato, Pedido, Tipo
from datetime import datetime
import bcrypt

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://KuanLefipe:SenhaFortona2035!@localhost/restaurante'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Função para obter o usuário logado a partir do header Authorization (Bearer <user_id>)
def get_cozinheiro_logado():
    auth = request.headers.get('Authorization')
    if not auth:
        return None
    try:
        token_type, user_id = auth.split()
        if token_type.lower() != 'bearer':
            return None
        user_id_int = int(user_id)
        return Cozinheiro.query.get(user_id_int)
    except Exception:
        return None

# --- Rotas Usuário ---

@app.route('/cadastro', methods=['POST'])
def cadastrar_cozinheiro():
    dados = request.json
    try:
        nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date()
    except (ValueError, KeyError):
        return jsonify({'erro': 'Data de nascimento inválida ou não informada'}), 400

    idade = Cozinheiro.calcular_idade(nascimento)
    senha = dados.get('senha', '')
    if not senha:
        return jsonify({'erro': 'Senha não informada'}), 400

    senha_bytes = senha.encode('utf-8')
    senha_criptografada = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

    novo_cozinheiro = Cozinheiro(
        nome=dados.get('nome'),
        email=dados.get('email'),
        cep=dados.get('cep'),
        cpf=dados.get('cpf'),
        data_nascimento=nascimento,
        idade=idade,
        senha_hash=senha_criptografada.decode('utf-8'),
        tipo='comum'
    )

    try:
        db.session.add(novo_cozinheiro)
        db.session.commit()
        return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar usuário'}), 500

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    cozinheiro = Cozinheiro.query.filter_by(email=dados.get('email')).first()

    if cozinheiro and bcrypt.checkpw(dados.get('senha', '').encode(), cozinheiro.senha_hash.encode()):
        return jsonify({
            'mensagem': 'Login bem-sucedido',
            'cozinheiro': {
                'id': cozinheiro.id,
                'nome': cozinheiro.nome,
                'email': cozinheiro.email,
                'cep': cozinheiro.cep,
                'cpf': cozinheiro.cpf,
                'data_nascimento': cozinheiro.data_nascimento.strftime('%Y-%m-%d'),
                'idade': cozinheiro.idade,
                'tipo': cozinheiro.tipo
            }
        }), 200

    return jsonify({'erro': 'E-mail ou senha inválidos'}), 401

@app.route('/cozinheiros/<int:id>', methods=['GET'])
def obter_cozinheiro(id):
    cozinheiro = Cozinheiro.query.get_or_404(id)
    cozinheiro_logado = get_cozinheiro_logado()
    if not cozinheiro_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    if cozinheiro_logado.id == cozinheiro.id or cozinheiro_logado.tipo == 'admin':
        return jsonify(cozinheiro.to_dict_completo())
    else:
        return jsonify(cozinheiro.to_dict_publico())

@app.route('/cozinheiros/me', methods=['GET'])
def obter_meu_perfil():
    cozinheiro_logado = get_cozinheiro_logado()
    if not cozinheiro_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    return jsonify(cozinheiro_logado.to_dict_completo())

@app.route('/cozinheiros/<int:id>', methods=['PUT'])
def atualizar_cozinheiro(id):
    cozinheiro_logado = get_cozinheiro_logado()
    if not cozinheiro_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    if cozinheiro_logado.id != id and cozinheiro_logado.tipo != 'admin':
        return jsonify({'erro': 'Acesso negado'}), 403

    dados = request.json
    cozinheiro = Cozinheiro.query.get_or_404(id)
    if 'nome' in dados:
        cozinheiro.nome = dados['nome']
    if 'email' in dados:
        cozinheiro.email = dados['email']

    try:
        db.session.commit()
        return jsonify({'mensagem': 'Dados atualizados com sucesso'})
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao atualizar usuário'}), 500

# --- Rotas tipo ---

@app.route('/tipos', methods=['GET'])
def listar_tipos():
    tipos = Tipo.query.all()
    return jsonify([{'id': c.id, 'nome': c.nome} for c in tipos])

@app.route('/tipos', methods=['POST'])
def criar_tipo():
    dados = request.json
    nome = dados.get('nome')
    if not nome:
        return jsonify({'erro': 'Nome da tipo é obrigatório'}), 400

    existente = Tipo.query.filter_by(nome=nome).first()
    if existente:
        return jsonify({'erro': 'tipo já existe'}), 400

    nova_tipo = Tipo(nome=nome)
    try:
        db.session.add(nova_tipo)
        db.session.commit()
        return jsonify({'mensagem': 'tipo criada', 'id': nova_tipo.id}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao criar tipo'}), 500

# --- Rotas prato ---

@app.route('/pratos', methods=['GET'])
def listar_pratos():
    pratos = Prato.query.all()
    return jsonify([{
        'id': p.id,
        'nome': p.nome,
        'preco': p.preco,
        'imagem_url': p.imagem_url,
        'peso': p.peso,
        'tipo': p.tipo.nome,
        'cozinheiro': p.cozinheiro.nome
    } for p in pratos])

@app.route('/pratos/<int:id>', methods=['GET'])
def obter_prato(id):
    p = Prato.query.get(id)
    if not p:
        return jsonify({'erro': 'prato não encontrado'}), 404
    return jsonify({
        'id': p.id,
        'nome': p.nome,
        'preco': p.preco,
        'imagem_url': p.imagem_url,
        'peso': p.peso,
        'tipo': {
            'id': p.tipo.id if p.tipo else None,
            'nome': p.tipo.nome if p.tipo else None
        },
        'cozinheiro': {
            'id': p.cozinheiro.id,
            'nome': p.cozinheiro.nome
        }
    })

@app.route('/pratos', methods=['POST'])
def criar_prato():
    cozinheiro_logado = get_cozinheiro_logado()
    if not cozinheiro_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    dados = request.json
    nome = dados.get('nome')
    preco = dados.get('preco')
    imagem_url = dados.get('imagem_url')
    peso = dados.get('peso')
    tipo_id = dados.get('tipo_id')

    if not nome or preco is None or not imagem_url or peso is None or not tipo_id:
        return jsonify({'erro': 'Dados incompletos'}), 400

    try:
        preco = float(preco)
        peso = float(peso)
        tipo_id = int(tipo_id)
        if peso <= 0:
            return jsonify({'erro': 'Peso deve ser maior que zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'erro': 'Preço, peso ou tipo inválidos'}), 400

    tipo = Tipo.query.get(tipo_id)
    if not tipo:
        return jsonify({'erro': 'tipo não encontrada'}), 404

    novo_prato = Prato(
        nome=nome,
        preco=preco,
        imagem_url=imagem_url,
        peso=peso,
        tipo_id=tipo_id,
        cozinheiro_id=cozinheiro_logado.id
    )

    try:
        db.session.add(novo_prato)
        db.session.commit()
        return jsonify({'mensagem': 'prato criado com sucesso!'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao salvar prato'}), 500

@app.route('/pratos/<int:id>', methods=['DELETE'])
def deletar_prato(id):
    cozinheiro_logado = get_cozinheiro_logado()
    if not cozinheiro_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    prato = Prato.query.get(id)
    if not prato:
        return jsonify({'erro': 'prato não encontrado'}), 404

    if cozinheiro_logado.id != prato.cozinheiro_id and cozinheiro_logado.tipo != 'admin':
        return jsonify({'erro': 'Acesso negado'}), 403

    try:
        Pedido.query.filter_by(prato_id=id).delete()
        db.session.delete(prato)
        db.session.commit()
        return jsonify({'mensagem': 'prato deletado com sucesso'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao deletar prato'}), 500

# --- pedido (sem usuário_id) ---

@app.route('/pedido', methods=['POST'])
def adicionar_ao_pedido():
    dados = request.json
    prato_id = dados.get('prato_id')
    prato = Prato.query.get(prato_id)
    if not prato:
        return jsonify({'erro': 'prato não encontrado'}), 404

    try:
        novo_item = Pedido(prato_id=prato.id)
        db.session.add(novo_item)
        db.session.commit()
        return jsonify({'mensagem': 'prato adicionado ao pedido!'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao adicionar pedido'}), 500

@app.route('/pedido', methods=['GET'])
def listar_pedido():
    itens = Pedido.query.all()
    pedido = []
    total = 0

    for item in itens:
        prato = Prato.query.get(item.prato_id)
        if prato:
            pedido.append({
                'id': prato.id,
                'nome': prato.nome,
                'preco': prato.preco,
                'imagem_url': prato.imagem_url,
                'peso': prato.peso,
                'tipo': prato.tipo.nome
            })
            total += prato.preco

    return jsonify({'pratos': pedido, 'valor_total': total})

@app.route('/pedido/<int:prato_id>', methods=['DELETE'])
def remover_do_pedido(prato_id):
    item = Pedido.query.filter_by(prato_id=prato_id).first()
    if not item:
        return jsonify({'erro': 'prato não está no pedido'}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'mensagem': 'prato removido do pedido!'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao remover prato'}), 500

@app.route('/pratos/cozinheiro/<int:cozinheiro_id>', methods=['GET'])
def pratos_por_cozinheiro(cozinheiro_id):
    pratos = Prato.query.filter_by(cozinheiro_id=cozinheiro_id).all()
    lista = []
    for p in pratos:
        lista.append({
            'id': p.id,
            'nome': p.nome,
            'preco': p.preco,
            'imagem_url': p.imagem_url,
            'peso': p.peso,
            'tipo': {
                'id': p.tipo.id if p.tipo else None,
                'nome': p.tipo.nome if p.tipo else None
            }
        })
    return jsonify(lista)


@app.route('/pratos/tipo/<int:tipo_id>', methods=['GET'])
def pratos_por_tipo(tipo_id):
    pratos = Prato.query.filter_by(tipo_id=tipo_id).all()
    lista = []
    for p in pratos:
        lista.append({
            'id': p.id,
            'nome': p.nome,
            'preco': p.preco,
            'imagem_url': p.imagem_url,
            'peso': p.peso,
            'tipo': {
                'id': p.tipo.id if p.tipo else None,
                'nome': p.tipo.nome if p.tipo else None
            }
        })
    return jsonify(lista)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
