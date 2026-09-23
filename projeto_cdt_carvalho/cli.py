import sys
from validators import validar_cpf, validar_email

def obter_dados_aluno():
    print("\n" + "="*40)
    print("   ACADEMIA FIT - CADASTRO VIA TERMINAL   ")
    print("="*40)

    nome = input("Digite o nome completo: ").strip()
    
    # Validação do CPF com loop (repete até digitar certo)
    while True:
        cpf = input("Digite o CPF: ").strip()
        if validar_cpf(cpf):
            print("✅ CPF válido!")
            break
        print("❌ CPF inválido! Tente novamente.")

    # Validação do E-mail com loop
    while True:
        email = input("Digite o e-mail: ").strip()
        if validar_email(email):
            print("✅ E-mail válido!")
            break
        print("❌ E-mail inválido! Tente novamente.")

    print("\nPlanos disponíveis:")
    print("1 - Mensal")
    print("2 - Trimestral")
    print("3 - Anual")
    plano_opcao = input("Escolha o plano (1, 2 ou 3): ").strip()

    planos = {"1": "mensal", "2": "trimestral", "3": "anual"}
    plano = planos.get(plano_opcao, "mensal")

    return {
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "plano": plano
    }

def menu_cli():
    while True:
        dados_aluno = obter_dados_aluno()

        # 3. Importação dinâmica e testes dos outros módulos
        print("\n[1/3] Salvando no banco de dados...")
        try:
            from database import salvar_aluno
            salvar_aluno(dados_aluno)
            print("✅ Salvo no banco com sucesso!")
        except Exception as e:
            print(f"⚠️ Módulo database.py pendente ou com erro: {e}")

        print("\n[2/3] Executando automação no site...")
        try:
            from selenium_bot import preencher_matricula
            preencher_matricula(dados_aluno)
            print("✅ Formulário web preenchido!")
        except Exception as e:
            print(f"⚠️ Módulo selenium_bot.py pendente ou com erro: {e}")

        print("\n[3/3] Gerando comprovante e log...")
        try:
            from receipt import gerar_comprovante_pdf, registrar_log
            gerar_comprovante_pdf(dados_aluno)
            registrar_log(f"Cadastro do aluno {dados_aluno['nome']} finalizado.")
            print("✅ Comprovante gerado!")
        except Exception as e:
            print(f"⚠️ Módulo receipt.py pendente ou com erro: {e}")

        print("\n" + "="*40)
        print("      PROCESSO CONCLUÍDO COM SUCESSO!     ")
        print("="*40)

        opcao = input("\nDeseja realizar outro cadastro? (s/n): ").strip().lower()
        if opcao != 's':
            print("\nEncerrando o sistema...")
            break

if __name__ == "__main__":
    menu_cli()