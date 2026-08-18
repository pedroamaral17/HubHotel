# IMPORTS

from datetime import date
from supabase import create_client, Client

# -- CONEXÃO COM O SUPABASE

url = "https://qffvoexhsofrltsqctzb.supabase.co"
key = "sb_publishable_r9yoMcNyBynwEM3CX0d9zQ_qJlycbuG"

supabase: Client = create_client(url, key)


# ============================================================
#                       1. BUSCAR HOTEL
# ============================================================

def buscar_hotel(nome_busca: str, endereco_busca: str):
    resposta = (
        supabase.table("hotel")
        .select("*")
        .ilike("nome", f"%{nome_busca}%")
        .ilike("endereco", f"%{endereco_busca}%")
        .execute()
    )
    return resposta.data


# ============================================================
# 2. TIPOS DE QUARTO DE UM HOTEL (+ amenidades de cada um)
# ============================================================

def buscar_tipos_quarto(id_hotel: int):
    resposta = (
        supabase.table("tipo_quarto")
        .select("*")
        .eq("id_hotel", id_hotel)
        .execute()
    )
    return resposta.data


def buscar_amenidades_do_tipo(id_tipo_quarto: int):
    # A ligação só guarda os IDs, então busco os nomes depois
    resposta = (
        supabase.table("tipo_quarto_amenidade")
        .select("id_amenidade")
        .eq("id_tipo_quarto", id_tipo_quarto)
        .execute()
    )
    ids_amenidades = [linha["id_amenidade"] for linha in resposta.data]

    if not ids_amenidades:
        return []

    resposta_amenidades = (
        supabase.table("amenidade_do_quarto")
        .select("nome_amenidade")
        .in_("id_amenidade", ids_amenidades)
        .execute()
    )
    return [linha["nome_amenidade"] for linha in resposta_amenidades.data]


# ============================================================
#               3. QUARTOS DISPONÍVEIS DE UM TIPO
# ============================================================

def buscar_id_status(palavra_chave: str):
    # Busco o status por trecho do nome (ex: "dispon" acha "Disponível")
    resposta = (
        supabase.table("status_quarto")
        .select("id_status")
        .ilike("nome_status", f"%{palavra_chave}%")
        .execute()
    )
    if not resposta.data:
        return None
    return resposta.data[0]["id_status"]


def buscar_quartos_disponiveis(id_tipo_quarto: int):
    id_status_disponivel = buscar_id_status("dispon")

    resposta = (
        supabase.table("quarto")
        .select("*")
        .eq("id_tipo_quarto", id_tipo_quarto)
        .eq("id_status", id_status_disponivel)
        .execute()
    )
    return resposta.data


def atualizar_status_quarto(id_quarto: int, id_status: int):
    (
        supabase.table("quarto")
        .update({"id_status": id_status})
        .eq("id_quarto", id_quarto)
        .execute()
    )


# ============================================================
#        4. HÓSPEDE (buscar por CPF ou cadastrar novo)
# ============================================================

def buscar_hospede_por_documento(documento: str):
    # Procuro tanto em cpf quanto em cnpj, não sei de antemão qual é
    resposta = (
        supabase.table("hospede")
        .select("*")
        .or_(f"cpf.eq.{documento},cnpj.eq.{documento}")
        .execute()
    )
    if resposta.data:
        return resposta.data[0]
    return None


def cadastrar_hospede_pf(nome: str, cpf: str, email: str, fone: str, data_nascimento: str):
    resposta = (
        supabase.table("hospede")
        .insert({
            "nome": nome,
            "cpf": cpf,
            "cnpj": None,
            "tipo_pessoa": "PF",
            "email": email,
            "fone": fone,
            "data_nascimento": data_nascimento,
        })
        .execute()
    )
    return resposta.data[0]


def cadastrar_hospede_pj(razao_social: str, cnpj: str, email: str, fone: str):
    resposta = (
        supabase.table("hospede")
        .insert({
            "nome": razao_social,
            "cpf": None,
            "cnpj": cnpj,
            "tipo_pessoa": "PJ",
            "email": email,
            "fone": fone,
        })
        .execute()
    )
    return resposta.data[0]


# ============================================================
#                    5. RESERVA E PAGAMENTO
# ============================================================

def criar_reserva(id_hospede: int, id_quarto: int, checkin: str, checkout: str, valor_total: float):
    resposta = (
        supabase.table("reserva")
        .insert({
            "hospede": id_hospede,
            "quarto": id_quarto,
            "checkin": checkin,
            "checkout": checkout,
            "valor_total": valor_total,
            "status": True,  # True = reserva ativa/confirmada
        })
        .execute()
    )
    return resposta.data[0]


def criar_pagamento(numero_reserva: int, valor_total: float, formato: str):
    resposta = (
        supabase.table("pagamento")
        .insert({
            "reserva": numero_reserva,
            "valor_total": valor_total,
            "formato": formato,
            "status": "pendente",
        })
        .execute()
    )
    return resposta.data[0]


# ============================================================
#                      FLUXO PRINCIPAL
# ============================================================

def main():
    # -- 1. Buscar hotel
    nome = input("Nome do hotel: ")
    endereco = input("Endereço: ")

    hoteis = buscar_hotel(nome, endereco)

    if not hoteis:
        print("Nenhum hotel encontrado.")
        return

    for i, hotel in enumerate(hoteis):
        print(f"[{i}] {hotel['nome']} - {hotel['endereco']}")

    escolha = int(input("Escolha o hotel (número da lista): "))
    hotel_escolhido = hoteis[escolha]

    # -- 2. Listar tipos de quarto + amenidades
    tipos = buscar_tipos_quarto(hotel_escolhido["id_hotel"])

    if not tipos:
        print("Este hotel não possui tipos de quarto cadastrados.")
        return

    for i, tipo in enumerate(tipos):
        amenidades = buscar_amenidades_do_tipo(tipo["id_tipo_quarto"])
        print(f"[{i}] {tipo['nome_tipo']} - R$ {tipo['preco_diaria']}/diária")
        print(f"    Amenidades: {', '.join(amenidades) if amenidades else 'nenhuma'}")

    escolha = int(input("Escolha o tipo de quarto (número da lista): "))
    tipo_escolhido = tipos[escolha]

    # -- 3. Quartos disponíveis
    quartos = buscar_quartos_disponiveis(tipo_escolhido["id_tipo_quarto"])

    if not quartos:
        print("Não há quartos disponíveis para este tipo.")
        return

    for i, quarto in enumerate(quartos):
        print(f"[{i}] Quarto {quarto['numero']}")

    escolha = int(input("Escolha o quarto (número da lista): "))
    quarto_escolhido = quartos[escolha]

    # -- 4. Hóspede: PF ou PJ, busca por documento, cadastra se não existir
    tipo_pessoa = input("Pessoa física ou jurídica? (PF/PJ): ").strip().upper()
    documento = input("CPF: " if tipo_pessoa == "PF" else "CNPJ: ")

    hospede = buscar_hospede_por_documento(documento)

    if hospede is None:
        print("Hóspede não encontrado, vamos cadastrar.")
        email = input("Email: ")
        fone = input("Telefone: ")

        if tipo_pessoa == "PF":
            nome_hospede = input("Nome: ")
            data_nascimento = input("Data de nascimento (AAAA-MM-DD): ")
            hospede = cadastrar_hospede_pf(nome_hospede, documento, email, fone, data_nascimento)
        else:
            razao_social = input("Razão social: ")
            hospede = cadastrar_hospede_pj(razao_social, documento, email, fone)

    # -- 5. Checkin, checkout e valor total
    checkin_str = input("Data de check-in (AAAA-MM-DD): ")
    checkout_str = input("Data de check-out (AAAA-MM-DD): ")

    checkin = date.fromisoformat(checkin_str)
    checkout = date.fromisoformat(checkout_str)

    if checkout <= checkin:
        print("A data de check-out precisa ser depois do check-in.")
        return

    diarias = (checkout - checkin).days
    valor_total = diarias * float(tipo_escolhido["preco_diaria"])

    reserva = criar_reserva(
        hospede["id_hospede"],
        quarto_escolhido["id_quarto"],
        checkin_str,
        checkout_str,
        valor_total,
    )

    # -- 6. Atualiza o status do quarto para "reservado"
    id_status_reservado = buscar_id_status("reserv")
    if id_status_reservado:
        atualizar_status_quarto(quarto_escolhido["id_quarto"], id_status_reservado)

    # -- 7. Pagamento
    formato = input("Forma de pagamento (pix, cartao, dinheiro): ")
    pagamento = criar_pagamento(reserva["numero"], valor_total, formato)

    print("-" * 30)
    print("Reserva realizada com sucesso!")
    print(f"Número da reserva: {reserva['numero']}")
    print(f"Valor total: R$ {valor_total}")
    print(f"Pagamento registrado: {pagamento['id_pagamento']} ({formato})")


if __name__ == "__main__":
    main()