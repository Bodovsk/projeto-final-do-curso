import hashlib
from datetime import datetime
from typing import Dict, Literal, Optional, TypedDict

# ========== TIPOS ==========
NIVEL_ACESSO = Literal["BATMAN", "ADMIN", "FUNCIONARIO"]
NIVEL_BATMAN: NIVEL_ACESSO = "BATMAN"
NIVEL_ADMIN: NIVEL_ACESSO = "ADMIN"
NIVEL_FUNCIONARIO: NIVEL_ACESSO = "FUNCIONARIO"

class Usuario(TypedDict):
    nome: str
    senha_hash: str
    nivel: NIVEL_ACESSO
    alias: str
    email: Optional[str]
    ultimo_acesso: Optional[str]
    data_criacao: Optional[str]

class Equipamento(TypedDict):
    nome: str
    tipo: str
    status: str
    localizacao: str
    ultima_manutencao: Optional[str]

# ========== BANCO DE DADOS ==========
USUARIOS: Dict[str, Usuario] = {
    "WAYNE-001": {
        "nome": "Bruce Wayne",
        "senha_hash": hashlib.sha256(b"i_am_batman").hexdigest(),
        "nivel": NIVEL_BATMAN,
        "alias": "Batman",
        "email": "bruce@wayne.com",
        "ultimo_acesso": None,
        "data_criacao": "2023-01-01"
    },
    "WAYNE-002": {
        "nome": "Alfred Pennyworth",
        "senha_hash": hashlib.sha256(b"alfred321").hexdigest(),
        "nivel": NIVEL_ADMIN,
        "alias": "Alfred",
        "email": "alfred@wayne.com",
        "ultimo_acesso": None,
        "data_criacao": "2023-01-01"
    },
    "WAYNE-003": {
        "nome": "Dick Grayson",
        "senha_hash": hashlib.sha256(b"boy_wonder").hexdigest(),
        "nivel": NIVEL_FUNCIONARIO,
        "alias": "Robin",
        "email": "dick.grayson@wayne.com",
        "ultimo_acesso": None,
        "data_criacao": "2023-01-01"
    }
}

EQUIPAMENTOS: Dict[str, Equipamento] = {
    "BAT-001": {
        "nome": "Bat-Grapple",
        "tipo": "Ferramenta",
        "status": "Operacional",
        "localizacao": "Batcaverna",
        "ultima_manutencao": datetime.now().strftime("%Y-%m-%d")
    }
}

AREAS: Dict[str, NIVEL_ACESSO] = {
    "Batcaverna": NIVEL_BATMAN,
    "Laboratório": NIVEL_ADMIN,
    "Arsenal": NIVEL_ADMIN,
    "Sala de Monitoramento": NIVEL_ADMIN,
    "Recepção": NIVEL_FUNCIONARIO
}

# ========== FUNÇÕES PRINCIPAIS ==========
def verificar_credenciais(id_usuario: str, senha: str) -> bool:
    """Verifica se as credenciais são válidas com tratamento de erros"""
    usuario = USUARIOS.get(id_usuario)
    if not usuario:
        return False
    try:
        return usuario["senha_hash"] == hashlib.sha256(senha.encode()).hexdigest()
    except Exception:
        return False

def obter_usuario(id_usuario: str) -> Optional[Usuario]:
    """Retorna dados do usuário sem informações sensíveis"""
    if usuario := USUARIOS.get(id_usuario):
        return {
            "nome": usuario["nome"],
            "nivel": usuario["nivel"],
            "alias": usuario["alias"],
            "email": usuario.get("email"),
            "ultimo_acesso": usuario.get("ultimo_acesso")
        }
    return None

def atualizar_ultimo_acesso(id_usuario: str) -> None:
    """Registra o último acesso do usuário"""
    if id_usuario in USUARIOS:
        USUARIOS[id_usuario]["ultimo_acesso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def verificar_acesso_area(id_usuario: str, area: str) -> bool:
    """Verifica se usuário tem acesso a uma área específica"""
    usuario = USUARIOS.get(id_usuario)
    if not usuario or area not in AREAS:
        return False
    return usuario["nivel"] == AREAS[area]

# ========== FUNÇÕES DE EQUIPAMENTOS ==========
def listar_equipamentos() -> Dict[str, Equipamento]:
    """Retorna todos os equipamentos"""
    return EQUIPAMENTOS

def adicionar_equipamento(dados: Equipamento) -> str:
    """Adiciona novo equipamento e retorna ID"""
    novo_id = f"BAT-{len(EQUIPAMENTOS)+1:03d}"
    EQUIPAMENTOS[novo_id] = dados
    return novo_id