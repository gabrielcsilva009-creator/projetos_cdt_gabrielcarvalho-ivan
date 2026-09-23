import re
from datetime import datetime

def validar_nome(nome: str) -> bool:
    """Valida se o nome tem ao menos duas palavras e apenas letras/espaços."""
    nome = nome.strip()
    partes = nome.split()
    if len(partes) < 2:
        return False
    nome_sem_espaco = nome.replace(" ", "")
    return nome_sem_espaco.isalpha()

def validar_cpf(cpf: str) -> bool:
    """Remove caracteres não numéricos e verifica se tem 11 dígitos."""
    cpf_limpo = re.sub(r'\D', '', cpf)
    return len(cpf_limpo) == 11

def limpar_cpf(cpf: str) -> str:
    """Remove pontuações do CPF."""
    return re.sub(r'\D', '', cpf)

def formatar_cpf(cpf: str) -> str:
    """Formata o CPF para o padrão 000.000.000-00."""
    cpf_limpo = limpar_cpf(cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf

def validar_email(email: str) -> bool:
    """Verifica o formato do e-mail usando expressão regular."""
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(padrao, email.strip()))

def validar_telefone(telefone: str) -> bool:
    """Verifica se tem 10 ou 11 dígitos (com DDD)."""
    tel_limpo = re.sub(r'\D', '', telefone)
    return len(tel_limpo) in (10, 11)

def limpar_telefone(telefone: str) -> str:
    """Remove caracteres não numéricos do telefone."""
    return re.sub(r'\D', '', telefone)

def validar_data_nascimento(data_str: str) -> bool:
    """Valida se a data está no formato DD/MM/AAAA."""
    try:
        datetime.strptime(data_str.strip(), "%d/%m/%Y")
        return True
    except ValueError:
        return False