from validadores import isCpfValid, isDdnValid, isEmailValid, isTelValid, hash_senha, IsSenhaValid
from integracao import integracao
from login import login


def cadastrar_usuario():
    while True:
        nome = input("Digite seu nome: ").strip()
        # FIX: "nome == int" nunca era True (comparava string com a classe int).
        # Trocado por uma checagem real: nome vazio ou só números.
        # correção com auxilio de IA
        if nome == "" or nome.isdigit():
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

    while True:
        senha = input("Digite sua senha(mínimo 8 caracteres): ").strip()
        if IsSenhaValid(senha):
            break
        else:
            print("Sua senha é muito curta, tente novamente.")

    usuario = {
        "nome": nome,
        "cpf": cpf,
        "data_nascimento": ddn,
        "email": email,
        "fone": telefone,
        # FIX: senha agora vai com hash (PBKDF2 + salt) pro banco,
        # nunca mais em texto puro
        # correção com auxilio de IA
        "senha_hash": hash_senha(senha),
    }

    try:
        # FIX: removido o print(usuario) — imprimia CPF, e-mail e a senha
        # (mesmo com hash, não há motivo pra jogar isso no console/log)
        # correção com auxilio de IA
        response = integracao.table("hospede").insert(usuario).execute()
        print("Usuário cadastrado com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")


print("=" * 20)
print("Bem-vindo ao HubHotel")
print("=" * 20)

while True:
    print("1 - Cadastrar conta\n2 - Login\n3 - Sair")

    # FIX: int(input()) quebrava com entrada não-numérica; agora valida antes
    # correção com auxilio de IA
    opcao_str = input("Digite a opção desejada: ").strip()
    if not opcao_str.isdigit():
        print("Opção inválida, digite um número.")
        continue
    opcao = int(opcao_str)

    match opcao:
        case 1:
            cadastrar_usuario()
        case 2:
            login()
        case 3:
            print("Saindo do programa.")
            break
        case _:
            print("Opção inválida.")