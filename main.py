from System.cadastro import cadastrar_usuario
from System.login import login
from System.reservas import menu_reservas
import questionary

print("=" * 20)
print("Bem-vindo ao HubHotel")
print("=" * 20)

while True:
    opcao = questionary.select(
        "O que deseja fazer?",
        choices=[
            questionary.Choice(title="Cadastrar conta", value="cadastro"),
            questionary.Choice(title="Login", value="login"),
            questionary.Choice(title="Sair", value="sair"),
        ],
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()

    if opcao is None or opcao == "sair":
        print("Saindo do programa.")
        break

    if opcao == "cadastro":
        usuario = cadastrar_usuario()
        if usuario:
            menu_reservas(usuario)
    elif opcao == "login":
        usuario = login()
        if usuario:
            menu_reservas(usuario)