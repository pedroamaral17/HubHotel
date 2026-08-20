from integracao import integracao
from validadores import checar_senha

usuario_logado = None


def login():
    global usuario_logado

    print("\n=== LOGIN ===")
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()

    # FIX: antes o login procurava numa lista local `usuarios` que nunca era
    # preenchida (o cadastro só inseria no Supabase, nunca nessa lista).
    # Ou seja: ninguém que se cadastrava conseguia logar. Agora busca direto
    # no banco pelo e-mail.
    try:
        response = integracao.table("hospede").select("*").eq("email", email).execute()
    except Exception as e:
        print(f"Erro ao consultar: {e}")
        return None

    if not response.data:
        print("\nEmail ou senha incorretos.")
        return None

    usuario = response.data[0]

    # FIX: comparação de senha em texto puro trocada por checar_senha,
    # que confere o hash salvo (ver hash_senha em validadores.py)
    if checar_senha(senha, usuario["senha_hash"]):
        usuario_logado = usuario
        print(f"\nBem-vindo(a), {usuario['nome']}!")
        return usuario

    print("\nEmail ou senha incorretos.")
    return None