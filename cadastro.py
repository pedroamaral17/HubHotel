from datetime import datetime
import re
from validadores import isCpfValid, isDdnValid, isEmailValid, isTelValid

hospede = []

def cadastrar_usuario():
    while True:
        nome = input("Digite seu nome: ").strip()
        if nome == "" or nome == int:
            print("Nome inválido, tente novamente.")
        else:
            break

    while True:
        cpf = input("Digite seu CPF(000.000.000-00): ")
        if isCpfValid(cpf):
            break
        else:
            print("CPF inválido, tente novamente.")

    while True:
        ddn = input("Digite sua data de nascimento(aaaa-mm-dd): ").strip()

        if isDdnValid(ddn):
            break
        else:
            print("Erro, tente novamente!")


    while True:
        email = input("Digite seu E-mail: ").strip()

        if isEmailValid(email):
            break
        else:
            print("Erro, tente novamente.")

    while True:
      telefone = input("Digite seu telefone: ").strip()

      if isTelValid(telefone):
          break
      else:
        print("Erro, tente novamente.")

    usuario = {
    "nome": nome,
    "cpf": cpf,
    "data_nascimento": ddn,
    "email": email,
    "fone": telefone
}

    try:
        print(usuario)
        response = supabase.table("hospede").insert(usuario).execute()
        print("Usuário cadastrado com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")




print("=" * 20)
print("Bem-vindo ao HubHotel")
print("=" * 20)

while True:
    print("1 - Login\n2 - Cadastrar conta\n3 - Sair")

    opcao = int(input("Digite a opção desejada: "))

    match opcao:
        case 1:
            print("Opção de login selecionada.")
        case 2:
            print("Opção de cadastro selecionada.")
            cadastrar_usuario()
        case 3:
            print("Saindo do programa.")
            break