import sqlite3

def inicializar_banco():
    """Cria a tabela de alunos no banco de dados SQLite se ela não existir."""
    conn = sqlite3.connect("academia.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT,
            email TEXT,
            telefone TEXT,
            data_nascimento TEXT,
            plano TEXT,
            status TEXT DEFAULT 'pendente'
        )
    """)
    
    conn.commit()
    conn.close()

def cpf_ja_cadastrado(cpf: str) -> bool:
    """Verifica se o CPF informado já está gravado no banco de dados."""
    conn = sqlite3.connect("academia.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM alunos WHERE cpf = ?", (cpf,))
    resultado = cursor.fetchone()
    
    conn.close()
    return resultado is not None

def salvar_aluno(dados: dict) -> int:
    """Insere os dados completos do aluno no banco e retorna o ID gerado."""
    conn = sqlite3.connect("academia.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO alunos (nome, cpf, email, telefone, data_nascimento, plano, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pendente')
    """, (
        dados.get('nome'),
        dados.get('cpf'),
        dados.get('email'),
        dados.get('telefone'),
        dados.get('data_nascimento'),
        dados.get('plano')
    ))
    
    # Pega o ID gerado automaticamente para o aluno
    aluno_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return aluno_id

def atualizar_status(aluno_id: int, status: str):
    """Atualiza o status do aluno (ex: 'confirmado' ou 'falha_automacao')."""
    conn = sqlite3.connect("academia.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE alunos
        SET status = ?
        WHERE id = ?
    """, (status, aluno_id))
    
    conn.commit()
    conn.close()