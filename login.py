from integracao import integracao
from validadores import checar_senha

usuario_logado = None


def login():
    global usuario_logado

    print("\n=== LOGIN ===")
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()

    try:
        response = integracao.table("hospede").select("*").eq("email", email).execute()
    except Exception as e:
        print(f"Erro ao consultar: {e}")
        return None

    if not response.data:
        print("\nEmail ou senha incorretos.")
        return None

    usuario = response.data[0]

    if checar_senha(senha, usuario["senha_hash"]):
        usuario_logado = usuario
        print(f"\nBem-vindo(a), {usuario['nome']}!")
        return usuario

    print("\nEmail ou senha incorretos.")
    return None