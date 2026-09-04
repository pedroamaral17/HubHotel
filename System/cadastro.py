from System.validadores import isCpfValid, isCnpjValid, isDdnValid, isEmailValid, isTelValid, hash_senha, IsSenhaValid
from System.integracao import integracao


def cadastrar_usuario():
    while True:
        tipo_pessoa = input("Cadastro para Pessoa Física ou Jurídica? (PF/PJ): ").strip().upper()
        if tipo_pessoa in ("PF", "PJ"):
            break
        print("Opção inválida, digite PF ou PJ.")

    if tipo_pessoa == "PF":
        return cadastrar_pf()
    else:
        return cadastrar_pj()


def cadastrar_pf():
    while True:
        nome = input("Digite seu nome: ").strip()
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

    email = _pedir_email()
    telefone = _pedir_telefone()
    senha = _pedir_senha()

    usuario = {
        "nome": nome,
        "cpf": cpf,
        "cnpj": None,
        "tipo_pessoa": "PF",
        "data_nascimento": ddn,
        "email": email,
        "fone": telefone,
        "senha_hash": hash_senha(senha),
    }

    return _salvar_usuario(usuario)


def cadastrar_pj():
    while True:
        razao_social = input("Digite a razão social da empresa: ").strip()
        if razao_social == "":
            print("Razão social inválida, tente novamente.")
        else:
            break

    while True:
        cnpj = input("Digite o CNPJ(00.000.000/0000-00): ")
        if isCnpjValid(cnpj):
            break
        else:
            print("CNPJ inválido, tente novamente.")

    email = _pedir_email()
    telefone = _pedir_telefone()
    senha = _pedir_senha()

    usuario = {
        "nome": razao_social,
        "cpf": None,
        "cnpj": cnpj,
        "tipo_pessoa": "PJ",
        "data_nascimento": None,
        "email": email,
        "fone": telefone,
        "senha_hash": hash_senha(senha),
    }

    return _salvar_usuario(usuario)


# ---- Campos em comum entre os PF e PJ ----

def _pedir_email():
    while True:
        email = input("Digite seu E-mail: ").strip()
        if isEmailValid(email):
            return email
        print("Erro, tente novamente.")


def _pedir_telefone():
    while True:
        telefone = input("Digite seu telefone: ").strip()
        if isTelValid(telefone):
            return telefone
        print("Erro, tente novamente.")


def _pedir_senha():
    while True:
        senha = input("Digite sua senha(mínimo 8 caracteres): ").strip()
        if IsSenhaValid(senha):
            return senha
        print("Sua senha é muito curta, tente novamente.")


def _salvar_usuario(usuario: dict):
    try:
        response = integracao.table("hospede").insert(usuario).execute()
        print("Usuário cadastrado com sucesso!")
        return response.data[0]
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return None