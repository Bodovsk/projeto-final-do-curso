from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime
from database import (
    verificar_credenciais,
    obter_usuario,
    atualizar_ultimo_acesso,
    verificar_acesso_area,
    listar_equipamentos,
    adicionar_equipamento,
    NIVEL_BATMAN,
    NIVEL_ADMIN,
    NIVEL_FUNCIONARIO
)

app = Flask(__name__, template_folder='../frontend/templates')
app.secret_key = 'sua_chave_secreta_super_segura'  # Em produção, use variáveis de ambiente!

# ========== DECORATORS ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Acesso não autorizado. Faça login primeiro.', 'erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def nivel_requerido(*niveis_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                flash('Acesso não autorizado. Faça login primeiro.', 'erro')
                return redirect(url_for('login'))
            
            usuario = obter_usuario(session.get('usuario_id'))
            if not usuario or usuario.get('nivel') not in niveis_permitidos:
                niveis = " ou ".join(niveis_permitidos)
                flash(f'Acesso restrito a: {niveis}', 'erro')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== ROTAS PRINCIPAIS ==========
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_usuario = request.form.get('id_wayne', '').strip()
        senha = request.form.get('senha', '').strip()
        
        if not id_usuario or not senha:
            flash('Preencha todos os campos', 'erro')
            return render_template('login.html')
        
        if not verificar_credenciais(id_usuario, senha):
            flash('Credenciais inválidas', 'erro')
            return render_template('login.html')
        
        # Atualiza acesso e configura sessão
        atualizar_ultimo_acesso(id_usuario)
        session['usuario_id'] = id_usuario
        usuario = obter_usuario(id_usuario)
        session['nivel_acesso'] = usuario['nivel']  # Armazena nível na sessão
        
        flash(f"Bem-vindo, {usuario['nome']}!", 'sucesso')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route("/dashboard")
@login_required
def dashboard():
    usuario = obter_usuario(session['usuario_id'])
    return render_template('dashboard.html', 
                         usuario=usuario,
                         nivel_acesso=usuario['nivel'])

@app.route("/logout", methods=['POST'])
def logout():
    if 'usuario_id' in session:
        session.clear()
        flash('Você foi desconectado com segurança', 'info')
    return redirect(url_for('login'))

# ========== ROTAS DE RECURSOS ==========
@app.route("/recursos")
@login_required
def recursos():
    usuario = obter_usuario(session['usuario_id'])
    if not verificar_acesso_area(usuario['nivel'], 'Laboratório'):
        flash('Acesso não autorizado a esta área', 'erro')
        return redirect(url_for('dashboard'))
    
    return render_template('resources.html', usuario=usuario)

# ========== ROTAS DE EQUIPAMENTOS ==========
@app.route("/recursos/equipamentos")
@login_required
@nivel_requerido(NIVEL_BATMAN, NIVEL_ADMIN)
def equipamentos():
    usuario = obter_usuario(session['usuario_id'])
    return render_template('recursos/equipamentos.html',
                         equipamentos=listar_equipamentos(),
                         usuario=usuario)

@app.route("/api/equipamentos", methods=['GET', 'POST'])
@login_required
@nivel_requerido(NIVEL_BATMAN, NIVEL_ADMIN)
def api_equipamentos():
    if request.method == 'POST':
        novo_equipamento = {
            "nome": request.json.get('nome'),
            "tipo": request.json.get('tipo'),
            "status": "Operacional",
            "localizacao": request.json.get('localizacao'),
            "ultima_manutencao": datetime.now().strftime("%Y-%m-%d")
        }
        equipamento_id = adicionar_equipamento(novo_equipamento)
        return jsonify({"status": "success", "id": equipamento_id})
    
    return jsonify(listar_equipamentos())

# ========== ROTAS DE DISPOSITIVOS ==========
@app.route("/recursos/dispositivos")
@login_required
@nivel_requerido(NIVEL_BATMAN, NIVEL_ADMIN)
def dispositivos():
    usuario = obter_usuario(session['usuario_id'])
    return render_template('recursos/dispositivos.html', usuario=usuario)

# ========== ROTAS DE VEÍCULOS ==========
@app.route("/recursos/veiculos")
@login_required
@nivel_requerido(NIVEL_BATMAN, NIVEL_ADMIN)
def veiculos():
    usuario = obter_usuario(session['usuario_id'])
    return render_template('recursos/veículos.html', usuario=usuario)

# ========== ROTAS PARA ADICIONAR NOVOS ITENS ==========

@app.route("/adicionar-dispositivo", methods=['GET', 'POST'])
@login_required
@nivel_requerido(NIVEL_BATMAN, NIVEL_ADMIN)
def adicionar_dispositivo():
    if request.method == 'POST':
        # Simples sistema de adição - você pode conectar ao banco de dados depois
        dispositivo = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'localizacao': request.form.get('localizacao'),
            'status': 'Operacional'
        }
        flash(f'Dispositivo {dispositivo["nome"]} adicionado com sucesso!', 'sucesso')
        return redirect(url_for('dispositivos'))
    
    return render_template('adicionar_dispositivos.html')

@app.route("/adicionar-veiculos", methods=['GET', 'POST'])
@login_required
@nivel_requerido(NIVEL_BATMAN, NIVEL_ADMIN)
def adicionar_veiculo():
    if request.method == 'POST':
        veiculo = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'identificacao': request.form.get('identificacao'),
            'status': 'Disponível'
        }
        flash(f'Veículo {veiculo["nome"]} adicionado com sucesso!', 'sucesso')
        return redirect(url_for('veiculos'))
    
    return render_template('adicionar_veiculos.html')

@app.route("/adicionar-equipamentos", methods=['GET', 'POST'])
@login_required
@nivel_requerido(NIVEL_BATMAN, NIVEL_ADMIN)
def adicionar_equipamento():
    if request.method == 'POST':
        equipamento = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'localizacao': request.form.get('localizacao'),
            'status': 'Operacional'
        }
        flash(f'Equipamento {equipamento["nome"]} adicionado com sucesso!', 'sucesso')
        return redirect(url_for('equipamentos'))
    
    return render_template('adicionar_equipamentos.html')

# ========== MANIPULADORES DE ERRO ==========
@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('erros/404.html'), 404

@app.errorhandler(403)
def acesso_negado(e):
    return render_template('erros/403.html'), 403

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)