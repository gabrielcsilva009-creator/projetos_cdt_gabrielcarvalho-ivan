"""
main_cli.py
Ponto de entrada do sistema de cadastro da FitFlow (versão CLI - Etapa 2).

Fluxo:
  1. Coleta os dados do aluno pelo terminal.
  2. Valida cada campo (validators.py).
  3. Salva no banco local SQLite (database.py).
  4. Aciona o robô Selenium para preencher o formulário (selenium_bot.py).
  5. Gera o comprovante em PDF e registra log (receipt.py).
"""

import sys

import database
import validators
from receipt import gerar_comprovante_pdf, registrar_log
from selenium_bot import preencher_matricula

PLANOS_VALIDOS = {"1": "mensal", "2": "trimestral", "3": "anual"}


def perguntar(mensagem: str, validador, mensagem_erro: str) -> str:
    while True:
        valor = input(mensagem).strip()
        if validador(valor):
            return valor
        print(f"  ⚠ {mensagem_erro}")


def escolher_plano() -> str:
    print("\nPlanos disponíveis:")
    print("  1 - Mensal")
    print("  2 - Trimestral")
    print("  3 - Anual")
    while True:
        escolha = input("Escolha o plano (1/2/3): ").strip()
        if escolha in PLANOS_VALIDOS:
            return PLANOS_VALIDOS[escolha]
        print("  ⚠ Opção inválida.")


def coletar_dados() -> dict:
    print("=== Cadastro de Aluno — FitFlow ===\n")

    nome = perguntar("Nome completo: ", validators.validar_nome,
                      "Digite nome e sobrenome, só letras.")

    while True:
        cpf = input("CPF (com ou sem pontuação): ").strip()
        if not validators.validar_cpf(cpf):
            print("  ⚠ CPF inválido.")
            continue
        cpf_limpo = validators.limpar_cpf(cpf)
        if database.cpf_ja_cadastrado(cpf_limpo):
            print("  ⚠ Este CPF já está cadastrado.")
            continue
        break

    email = perguntar("E-mail: ", validators.validar_email, "E-mail inválido.")
    telefone = perguntar("Telefone (com DDD): ", validators.validar_telefone,
                          "Telefone inválido (use DDD + número).")
    nascimento = perguntar("Data de nascimento (DD/MM/AAAA): ",
                            validators.validar_data_nascimento,
                            "Data inválida. Use o formato DD/MM/AAAA.")
    plano = escolher_plano()

    return {
        "nome": nome,
        "cpf": validators.formatar_cpf(cpf),
        "email": email,
        "telefone": validators.limpar_telefone(telefone),
        "data_nascimento": nascimento,
        "plano": plano,
    }


def main():
    database.inicializar_banco()

    dados = coletar_dados()

    aluno_id = database.salvar_aluno(dados)
    print(f"\n✔ Dados salvos localmente (ID {aluno_id}).")
    registrar_log(f"Aluno {aluno_id} ({dados['nome']}) salvo no banco local.")

    print("Abrindo navegador e preenchendo o formulário de matrícula...")
    sucesso = preencher_matricula({
        "nome": dados["nome"],
        "cpf": dados["cpf"],
        "email": dados["email"],
        "telefone": dados["telefone"],
        "data_nascimento": dados["data_nascimento"],
        "plano": dados["plano"],
    })

    if sucesso:
        database.atualizar_status(aluno_id, "confirmado")
        registrar_log(f"Aluno {aluno_id}: matrícula confirmada via Selenium.")
        print("✔ Matrícula confirmada no formulário!")
    else:
        database.atualizar_status(aluno_id, "falha_automacao")
        registrar_log(f"Aluno {aluno_id}: FALHA na automação (timeout ou elemento não encontrado).")
        print("⚠ Não foi possível confirmar a matrícula automaticamente. "
              "Os dados continuam salvos localmente — tente novamente mais tarde.")

    caminho_pdf = gerar_comprovante_pdf(dados, aluno_id)
    print(f"✔ Comprovante gerado em: {caminho_pdf}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCadastro cancelado pelo usuário.")
        sys.exit(0)