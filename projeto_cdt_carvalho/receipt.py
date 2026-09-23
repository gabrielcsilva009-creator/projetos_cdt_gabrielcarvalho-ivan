import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def registrar_log(mensagem: str):
    """Registra mensagens de log em um arquivo de texto local (sistema.log)."""
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha_log = f"[{data_hora}] {mensagem}\n"
    
    # Salva na mesma pasta em um arquivo de log
    with open("sistema.log", "a", encoding="utf-8") as arquivo:
        arquivo.write(linha_log)

def gerar_comprovante_pdf(dados: dict, aluno_id: int = None) -> str:
    """Gera um comprovante de matrícula oficial em PDF com os dados do aluno."""
    # Trata o nome do arquivo para evitar caracteres especiais
    nome_limpo = dados.get('nome', 'aluno').replace(' ', '_').lower()
    nome_arquivo = f"comprovante_{nome_limpo}.pdf"
    
    # Configuração do documento PDF (tamanho Letter)
    c = canvas.Canvas(nome_arquivo, pagesize=letter)
    largura, altura = letter
    
    # Cabeçalho do Comprovante
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 50, "ACADEMIA FIT - COMPROVANTE DE MATRÍCULA")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, altura - 70, f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if aluno_id:
        c.drawString(50, altura - 85, f"ID de Registro: {aluno_id}")
        
    # Linha divisória horizontal
    c.line(50, altura - 95, largura - 50, altura - 95)
    
    # Seção: Dados do Aluno
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, altura - 130, "Dados Cadastrados:")
    
    c.setFont("Helvetica", 11)
    c.drawString(70, altura - 160, f"Nome Completo: {dados.get('nome', '')}")
    c.drawString(70, altura - 185, f"CPF: {dados.get('cpf', '')}")
    c.drawString(70, altura - 210, f"E-mail: {dados.get('email', '')}")
    
    # Tratamento caso o telefone ou data de nascimento venham opcionais no dicionário
    if 'telefone' in dados and dados['telefone']:
        c.drawString(70, altura - 235, f"Telefone: {dados.get('telefone', '')}")
        offset = 25
    else:
        offset = 0
        
    plano_texto = dados.get('plano', '').capitalize()
    c.drawString(70, altura - (235 + offset), f"Plano Escolhido: {plano_texto}")
    
    # Rodapé institucional
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 50, "Este documento é um comprovante gerado automaticamente pelo sistema de automação FitFlow.")
    
    # Salva o arquivo PDF no disco
    c.save()
    
    # Retorna o caminho absoluto onde o PDF foi salvo
    return os.path.abspath(nome_arquivo)