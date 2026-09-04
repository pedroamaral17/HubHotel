from System.cadastro import cadastrar_usuario
from System.login import login
from System.reservas import iniciar_reserva

print("=" * 20)
print("Bem-vindo ao HubHotel")
print("=" * 20)

while True:
    print("1 - Cadastrar conta\n2 - Login\n3 - Sair")

    opcao_str = input("Digite a opção desejada: ").strip()
    if not opcao_str.isdigit():
        print("Opção inválida, digite um número.")
        continue
    opcao = int(opcao_str)

    match opcao:
        case 1:
            usuario = cadastrar_usuario()
            if usuario:
                iniciar_reserva(usuario)
        case 2:
            usuario = login()
            if usuario:
                iniciar_reserva(usuario)
        case 3:
            print("Saindo do programa.")
            break
        case _:
            print("Opção inválida.")