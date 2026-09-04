from supabase import create_client, Client

url = "https://qffvoexhsofrltsqctzb.supabase.co"
key = "sb_publishable_r9yoMcNyBynwEM3CX0d9zQ_qJlycbuG"

integracao: Client = create_client(url, key)