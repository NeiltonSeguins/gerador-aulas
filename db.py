import sqlite3
import hashlib

# Nome do banco
DB_NAME = "users.db"

def init_db():
    """Cria a tabela de usuários se não existir"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    
    # --- CRIA UM USUÁRIO PADRÃO PARA TESTE ---
    # Usuário: admin
    # Senha: 123
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ("admin", make_hash("123")))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Usuário já existe
    
    conn.close()

def make_hash(password):
    """Cria um hash simples da senha para não salvar em texto puro"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_user(username, password):
    """Verifica se o usuário e senha batem"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, make_hash(password)))
    data = c.fetchall()
    conn.close()
    return len(data) > 0