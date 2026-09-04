from datetime import datetime
import re
import hashlib
import os


def isCpfValid(cpf):
    if not isinstance(cpf, str):
        return False

    cpf = re.sub("[^0-9]", '', cpf)

    # FIX: usar set() em vez da cadeia gigante de "or ==" — mais legível e fácil de manter
    # correção com auxilio de IA
    cpfs_invalidos = {str(n) * 11 for n in range(10)}
    if cpf in cpfs_invalidos:
        return False

    if len(cpf) != 11:
        return False

    # FIX: soma/peso em vez de sum/weight (sum é builtin do Python)
    # correção com auxilio de IA
    soma = 0
    peso = 10
    for n in range(9):
        soma = soma + int(cpf[n]) * peso
        peso = peso - 1

    digito_verificador = 11 - soma % 11
    primeiro_digito = 0 if digito_verificador > 9 else digito_verificador

    soma = 0
    peso = 11
    for n in range(10):
        soma = soma + int(cpf[n]) * peso
        peso = peso - 1

    digito_verificador = 11 - soma % 11
    segundo_digito = 0 if digito_verificador > 9 else digito_verificador

    return cpf[-2:] == "%s%s" % (primeiro_digito, segundo_digito)


def isCnpjValid(cnpj):
    """ Se o CNPJ no formato brasileiro for válido, retorna True, senão False. """
    if not isinstance(cnpj, str):
        return False

    # FIX: variável renomeada de "cpf" para "cnpj_limpo" — o nome antigo confundia
    # com a função isCpfValid logo acima, mesmo sendo um CNPJ sendo tratado aqui
    # correção com auxilio de IA
    cnpj_limpo = re.sub("[^0-9]", '', cnpj)

    if len(cnpj_limpo) != 14:
        return False

    soma = 0
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for n in range(12):
        soma = soma + int(cnpj_limpo[n]) * peso[n]

    digito_verificador = soma % 11
    primeiro_digito = 0 if digito_verificador < 2 else 11 - digito_verificador

    soma = 0
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for n in range(13):
        soma = soma + int(cnpj_limpo[n]) * peso[n]

    digito_verificador = soma % 11
    segundo_digito = 0 if digito_verificador < 2 else 11 - digito_verificador

    return cnpj_limpo[-2:] == "%s%s" % (primeiro_digito, segundo_digito)


def isDdnValid(ddn):
    if ddn == "":
        return False
    try:
        datetime.strptime(ddn, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def isEmailValid(email):
    # FIX: antes só dava print e continuava pro regex (que ia retornar False mesmo
    # com "" — funcionava por acaso). Agora retorna direto, sem side-effect de print
    # dentro de uma função que deveria só validar.
    # correção com auxilio de IA
    if email == "":
        return False
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(regex, email))


def isTelValid(telefone):
    telefone = re.sub(r"\D", "", telefone)
    return len(telefone) in (10, 11) and len(set(telefone)) > 1


def IsSenhaValid(senha):
    return len(senha) >= 8


def hash_senha(senha):
    salt = os.urandom(16)
    hash_gerado = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 100000)
    return salt.hex() + ":" + hash_gerado.hex()


def checar_senha(senha_digitada, hash_salvo):
    salt_hex, hash_hex = hash_salvo.split(":")
    salt = bytes.fromhex(salt_hex)
    hash_esperado = bytes.fromhex(hash_hex)
    hash_teste = hashlib.pbkdf2_hmac("sha256", senha_digitada.encode(), salt, 100000)
    return hash_teste == hash_esperado