from System.integracao import integracao
from System.validadores import checar_senha
import questionary

usuario_logado = None


def login():
    global usuario_logado

    while True:
        print("\n=== LOGIN ===")
        email = input("Email: ").strip()
        senha = questionary.password("Senha: ").ask()

        usuario = _autenticar(email, senha)

        if usuario:
            usuario_logado = usuario
            print(f"\nBem-vindo(a), {usuario['nome']}!")
            return usuario

        print("\nEmail ou senha incorretos.")

        opcao = questionary.select(
            "O que deseja fazer?",
            choices=[
                questionary.Choice(title="Tentar novamente", value="retry"),
                questionary.Choice(title="Voltar ao menu", value="voltar"),
            ],
            instruction="(use as setas do teclado e Enter para confirmar)",
        ).ask()

        if opcao != "Retry":
            return None


def _autenticar(email, senha):
    try:
        response = integracao.table("hospede").select("*").eq("email", email).execute()
    except Exception as e:
        print(f"Erro ao consultar: {e}")
        return None

    if not response.data:
        return None

    usuario = response.data[0]

    if checar_senha(senha, usuario["senha_hash"]):
        return usuario

    return None