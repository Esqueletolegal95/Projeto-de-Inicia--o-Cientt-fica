import obsws_python as obs

print("Iniciando...")

try:
    ws = obs.ReqClient(
        host="localhost",
        port=4455,
        password="pedro123",
        timeout=3
    )
    print(">> Conectado ao OBS!")
except Exception as e:
    print(">> ERRO ao conectar:")
    print(e)
    exit()

print(">> Solicitando lista de inputs...")

try:
    resp = ws.get_input_list()
    print("Inputs encontrados:")
    for inp in resp.inputs:
        print(f"- {inp['inputName']} (tipo: {inp['inputKind']})")

except Exception as e:
    print(">> ERRO ao solicitar inputs:")
    print(e)

print("Fim.")
