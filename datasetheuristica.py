import json
catalogo_inversiones = {
    "cdt": [
        {"id": "CDT1", "entidad": "Bancolombia", "tasa": 0.112, "riesgo": "bajo", "minimo": 100000},
        {"id": "CDT2", "entidad": "Davivienda", "tasa": 0.110, "riesgo": "bajo", "minimo": 150000},
        {"id": "CDT3", "entidad": "BBVA", "tasa": 0.109, "riesgo": "bajo", "minimo": 200000},
        {"id": "CDT4", "entidad": "Banco de Bogotá", "tasa": 0.111, "riesgo": "bajo", "minimo": 100000},
        {"id": "CDT5", "entidad": "Banco Popular", "tasa": 0.108, "riesgo": "bajo", "minimo": 100000},
        {"id": "CDT6", "entidad": "Banco AV Villas", "tasa": 0.107, "riesgo": "bajo", "minimo": 100000},
        {"id": "CDT7", "entidad": "Banco Caja Social", "tasa": 0.113, "riesgo": "bajo", "minimo": 50000},
        {"id": "CDT8", "entidad": "Banco Itaú", "tasa": 0.114, "riesgo": "bajo", "minimo": 100000},
        {"id": "CDT9", "entidad": "Scotiabank Colpatria", "tasa": 0.115, "riesgo": "bajo", "minimo": 150000},
        {"id": "CDT10", "entidad": "Banco Falabella", "tasa": 0.116, "riesgo": "bajo", "minimo": 50000},
        {"id": "CDT11", "entidad": "Bancoomeva", "tasa": 0.109, "riesgo": "bajo", "minimo": 100000},
        {"id": "CDT12", "entidad": "Serfinanza", "tasa": 0.118, "riesgo": "bajo", "minimo": 50000},
        {"id": "CDT13", "entidad": "Finandina", "tasa": 0.119, "riesgo": "bajo", "minimo": 100000},
        {"id": "CDT14", "entidad": "Mibanco", "tasa": 0.117, "riesgo": "bajo", "minimo": 50000},
        {"id": "CDT15", "entidad": "Banco W", "tasa": 0.120, "riesgo": "bajo", "minimo": 50000},
    ],

    "fondos": [
        {"id": "F1", "nombre": "Fondo Balanceado A", "tasa": 0.135, "riesgo": "medio", "minimo": 50000},
        {"id": "F2", "nombre": "Fondo Balanceado B", "tasa": 0.132, "riesgo": "medio", "minimo": 50000},
        {"id": "F3", "nombre": "Fondo Renta Mixta", "tasa": 0.138, "riesgo": "medio", "minimo": 100000},
        {"id": "F4", "nombre": "Fondo Moderado Plus", "tasa": 0.140, "riesgo": "medio", "minimo": 80000},
        {"id": "F5", "nombre": "Fondo Conservador Pro", "tasa": 0.130, "riesgo": "medio", "minimo": 50000},
        {"id": "F6", "nombre": "Fondo Global LATAM", "tasa": 0.142, "riesgo": "medio", "minimo": 100000},
        {"id": "F7", "nombre": "Fondo Indexado COLCAP", "tasa": 0.145, "riesgo": "medio", "minimo": 70000},
        {"id": "F8", "nombre": "Fondo Crecimiento", "tasa": 0.150, "riesgo": "medio", "minimo": 120000},
        {"id": "F9", "nombre": "Fondo Estrategia Dinámica", "tasa": 0.148, "riesgo": "medio", "minimo": 90000},
        {"id": "F10", "nombre": "Fondo Renta Variable Local", "tasa": 0.152, "riesgo": "medio", "minimo": 100000},
        {"id": "F11", "nombre": "Fondo Internacional USD", "tasa": 0.149, "riesgo": "medio", "minimo": 150000},
        {"id": "F12", "nombre": "Fondo ESG Colombia", "tasa": 0.137, "riesgo": "medio", "minimo": 80000},
        {"id": "F13", "nombre": "Fondo Multiactivos", "tasa": 0.141, "riesgo": "medio", "minimo": 60000},
        {"id": "F14", "nombre": "Fondo Renta Fija Plus", "tasa": 0.128, "riesgo": "medio", "minimo": 50000},
        {"id": "F15", "nombre": "Fondo Estrategia Andina", "tasa": 0.146, "riesgo": "medio", "minimo": 100000},
    ],

    "acciones": [
        {"id": "A1", "empresa": "Ecopetrol", "tasa": 0.18, "riesgo": "alto", "minimo": 20000},
        {"id": "A2", "empresa": "Bancolombia", "tasa": 0.17, "riesgo": "alto", "minimo": 20000},
        {"id": "A3", "empresa": "Grupo Sura", "tasa": 0.19, "riesgo": "alto", "minimo": 20000},
        {"id": "A4", "empresa": "ISA", "tasa": 0.16, "riesgo": "alto", "minimo": 20000},
        {"id": "A5", "empresa": "Celsia", "tasa": 0.20, "riesgo": "alto", "minimo": 20000},
        {"id": "A6", "empresa": "Grupo Argos", "tasa": 0.185, "riesgo": "alto", "minimo": 20000},
        {"id": "A7", "empresa": "Nutresa", "tasa": 0.175, "riesgo": "alto", "minimo": 20000},
        {"id": "A8", "empresa": "Almacenes Éxito", "tasa": 0.165, "riesgo": "alto", "minimo": 20000},
        {"id": "A9", "empresa": "Terpel", "tasa": 0.182, "riesgo": "alto", "minimo": 20000},
        {"id": "A10", "empresa": "Canacol Energy", "tasa": 0.195, "riesgo": "alto", "minimo": 20000},
    ],

    "criptomoneda": [
        {"id": "C1", "token": "Bitcoin", "tasa": 0.30, "riesgo": "alto", "minimo": 10000},
        {"id": "C2", "token": "Ethereum", "tasa": 0.28, "riesgo": "alto", "minimo": 10000},
        {"id": "C3", "token": "Solana", "tasa": 0.35, "riesgo": "alto", "minimo": 10000},
        {"id": "C4", "token": "Cardano", "tasa": 0.25, "riesgo": "alto", "minimo": 10000},
        {"id": "C5", "token": "Polygon", "tasa": 0.27, "riesgo": "alto", "minimo": 10000},
        {"id": "C6", "token": "Chainlink", "tasa": 0.29, "riesgo": "alto", "minimo": 10000},
        {"id": "C7", "token": "Avalanche", "tasa": 0.33, "riesgo": "alto", "minimo": 10000},
        {"id": "C8", "token": "Litecoin", "tasa": 0.22, "riesgo": "alto", "minimo": 10000},
        {"id": "C9", "token": "Polkadot", "tasa": 0.31, "riesgo": "alto", "minimo": 10000},
        {"id": "C10", "token": "Uniswap", "tasa": 0.34, "riesgo": "alto", "minimo": 10000},
    ]
}
datos = []
for categoria, lista in catalogo_inversiones.items():
    for item in lista:
        item_copy = item.copy()
        item_copy['categoria'] = categoria
        datos.append(item_copy)

nombre_archivo = "dataset_catalogo_inversiones.jsonl"

print(f"Guardando dataset financiero en {nombre_archivo}...")

with open(nombre_archivo, 'w', encoding='utf-8') as f:
    for entrada in datos:
        json.dump(entrada, f, ensure_ascii=False)
        f.write('\n')

print("Archivo creado. La IA ahora tiene ejemplos de planificación financiera en Colombia.")