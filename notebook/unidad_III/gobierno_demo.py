"""Caso sintetico y controles compartidos por los notebooks de Unidad III."""

from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
import re
import sqlite3
from uuid import uuid4

import pandas as pd


FECHA_CORTE = pd.Timestamp("2026-10-06T12:00:00Z")
VERSION_CONTRATO = "1.0.0"
COLUMNAS_FUENTE = {
    "fila_fuente", "id_venta", "fecha_venta", "id_producto", "monto",
    "moneda", "email", "actualizado_en",
}


def crear_datos():
    """Retorna ventas ficticias, maestro y evidencia parcial independiente."""
    filas = [
        ("v01", "1", "2026-10-05", "101", "1500.00", " ars ", "uno@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v02", "2", "2026-10-05", "102", "200.00", "ARS", "dos@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v03", "2", "2026-10-05", "102", "250.00", "ARS", "dos@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v04", "3", "2026-02-29", "101", "300.00", "ARS", "tres@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v05", "4", "2026-10-05", "101", "-10.00", "ARS", "cuatro@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v06", "5", "2026-10-05", "101", "500.00", "BTC", "cinco@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v07", "6", "2026-10-05", "999", "600.00", "ARS", "seis@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v08", "7", "2026-10-05", "102", "700.00", "USD", "email-invalido", "2026-10-06T10:00:00Z"),
        ("v09", "8", "2026-09-30", "102", "800.00", "ARS", " ", "2026-10-01T10:00:00Z"),
        ("v10", "9", "2026-10-07", "101", "900.00", "ARS", None, "2026-10-06T10:00:00Z"),
        ("v11", "10", "2026-10-05", "101", "1000.00", "ARS", "diez@demo.invalid", "2026-10-06T10:00:00Z"),
        ("v12", " ", "2026-10-05", "101", "1200.00", "ARS", None, "2026-10-06T10:00:00Z"),
    ]
    ventas = pd.DataFrame(filas, columns=[
        "fila_fuente", "id_venta", "fecha_venta", "id_producto", "monto",
        "moneda", "email", "actualizado_en",
    ])
    productos = pd.DataFrame({"id_producto": [101, 102], "producto": ["Producto A", "Producto B"]})
    referencia = pd.DataFrame({"id_venta": [1, 10], "monto_centavos_referencia": [150000, 99900]})
    return ventas, productos, referencia


def esquema_valido(datos):
    return set(datos.columns) == COLUMNAS_FUENTE


def centavos(valor):
    try:
        numero = Decimal(str(valor).strip())
        if not numero.is_finite() or numero != numero.quantize(Decimal("0.01")):
            return None
        return int(numero * 100)
    except (InvalidOperation, ValueError, TypeError):
        return None


def entero_positivo(valor):
    texto = str(valor).strip()
    return int(texto) if re.fullmatch(r"[1-9][0-9]*", texto) else None


def normalizar(datos):
    if not esquema_valido(datos):
        raise ValueError("Deriva de esquema: revisar contrato antes de transformar")
    if datos["fila_fuente"].isna().any() or datos["fila_fuente"].duplicated().any():
        raise ValueError("La identificacion tecnica de origen debe ser unica y no nula")
    resultado = datos.copy(deep=True)
    for columna in ["id_venta", "id_producto"]:
        resultado[columna] = pd.array(resultado[columna].map(entero_positivo), dtype="Int64")
    resultado["monto_centavos"] = pd.array(resultado["monto"].map(centavos), dtype="Int64")
    resultado["fecha_venta"] = pd.to_datetime(resultado["fecha_venta"], format="%Y-%m-%d", errors="coerce", utc=True)
    resultado["actualizado_en"] = pd.to_datetime(resultado["actualizado_en"], format="ISO8601", errors="coerce", utc=True)
    resultado["moneda"] = resultado["moneda"].astype("string").str.strip().str.upper()
    resultado["email"] = resultado["email"].astype("string").str.strip().replace("", pd.NA)
    return resultado


def perfil(datos):
    filas = []
    for columna in datos.columns:
        serie = datos[columna]
        blancos = serie.astype("string").str.strip().eq("").fillna(False)
        faltantes = serie.isna() | blancos
        filas.append({
            "columna": columna, "tipo": str(serie.dtype), "filas": len(datos),
            "faltantes": int(faltantes.sum()), "distintos_no_nulos": int(serie.nunique()),
            "completitud_pct": 100 * (~faltantes).mean() if len(datos) else None,
        })
    return pd.DataFrame(filas)


def evaluar(datos, productos, referencia):
    """Evalua todas las filas; exactitud solo sobre evidencia disponible."""
    referencia = referencia.copy()
    if referencia["id_venta"].duplicated().any() or referencia["id_venta"].isna().any():
        raise ValueError("La referencia de exactitud tiene claves invalidas")
    if productos["id_producto"].duplicated().any() or productos["id_producto"].isna().any():
        raise ValueError("El maestro de productos tiene claves invalidas")
    verdad = datos["id_venta"].map(referencia.set_index("id_venta")["monto_centavos_referencia"])
    edad_horas = (FECHA_CORTE - datos["actualizado_en"]).dt.total_seconds() / 3600
    reglas = [
        ("DQ_ID", "completitud", "cuarentena", datos["id_venta"].notna(), None),
        ("DQ_UNICIDAD", "unicidad", "cuarentena", ~datos["id_venta"].duplicated(keep=False) & datos["id_venta"].notna(), None),
        ("DQ_FECHA", "validez", "cuarentena", datos["fecha_venta"].notna() & datos["fecha_venta"].le(FECHA_CORTE), None),
        ("DQ_MONTO", "validez", "cuarentena", datos["monto_centavos"].notna() & datos["monto_centavos"].gt(0), None),
        ("DQ_MONEDA", "integridad", "cuarentena", datos["moneda"].isin(["ARS", "USD", "EUR"]), None),
        ("DQ_FK_PRODUCTO", "integridad", "cuarentena", datos["id_producto"].isin(productos["id_producto"]), None),
        ("DQ_ACTUALIZACION", "consistencia", "cuarentena", datos["actualizado_en"].notna() & datos["actualizado_en"].le(FECHA_CORTE) & datos["actualizado_en"].ge(datos["fecha_venta"]), None),
        ("DQ_EMAIL", "validez", "advertencia", datos["email"].str.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+").fillna(False), None),
        ("DQ_VIGENCIA", "vigencia", "advertencia", edad_horas.between(0, 48), None),
        ("DQ_EXACTITUD", "exactitud", "advertencia", datos["monto_centavos"].eq(verdad), verdad.notna()),
    ]
    detalle, resumen = [], []
    for regla_id, dimension, accion, cumple, elegible in reglas:
        elegible = pd.Series(True, index=datos.index) if elegible is None else elegible
        cumple = cumple.fillna(False)
        falla = elegible & ~cumple
        evaluados = int(elegible.sum())
        fallidos = int(falla.sum())
        resumen.append({
            "regla": regla_id, "dimension": dimension, "accion": accion,
            "evaluados": evaluados, "fallidos": fallidos,
            "no_evaluables": len(datos) - evaluados,
            "cumplimiento_pct": 100 * (evaluados - fallidos) / evaluados if evaluados else None,
            "owner": "Gerencia Comercial", "contrato": VERSION_CONTRATO,
        })
        for fila_fuente in datos.loc[falla, "fila_fuente"]:
            detalle.append({"fila_fuente": fila_fuente, "regla": regla_id, "accion": accion})
    detalle = pd.DataFrame(detalle, columns=["fila_fuente", "regla", "accion"])
    ids_rechazados = set(detalle.loc[detalle["accion"].eq("cuarentena"), "fila_fuente"])
    rechazadas = datos[datos["fila_fuente"].isin(ids_rechazados)].copy()
    aceptadas = datos[~datos["fila_fuente"].isin(ids_rechazados)].copy()
    assert len(datos) == len(aceptadas) + len(rechazadas)
    return aceptadas, rechazadas, pd.DataFrame(resumen), detalle


def puerta_publicacion(total, rechazadas, max_rechazo=0.20):
    if not 0 <= max_rechazo <= 1 or total < 0 or not 0 <= rechazadas <= total:
        raise ValueError("Parametros invalidos para la puerta de publicacion")
    return total > 0 and rechazadas < total and rechazadas / total <= max_rechazo


def huella(datos):
    contenido = datos.to_json(orient="split", date_format="iso", index=False)
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def nueva_conexion():
    conexion = sqlite3.connect(":memory:")
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.executescript("""
        CREATE TABLE productos (id_producto INTEGER PRIMARY KEY, producto TEXT NOT NULL);
        CREATE TABLE ventas (
            id_venta INTEGER PRIMARY KEY,
            id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
            fecha_venta TEXT NOT NULL,
            monto_centavos INTEGER NOT NULL CHECK (monto_centavos > 0),
            moneda TEXT NOT NULL CHECK (moneda IN ('ARS', 'USD', 'EUR')),
            fila_fuente TEXT NOT NULL,
            lote_inicial TEXT NOT NULL
        );
        CREATE TABLE lotes (
            lote TEXT PRIMARY KEY, huella TEXT NOT NULL, contrato TEXT NOT NULL,
            estado TEXT NOT NULL, total INTEGER NOT NULL, aceptadas INTEGER NOT NULL,
            rechazadas INTEGER NOT NULL, nuevas INTEGER NOT NULL, existentes INTEGER NOT NULL
        );
        CREATE TABLE hallazgos (
            lote TEXT NOT NULL REFERENCES lotes(lote), fila_fuente TEXT NOT NULL,
            regla TEXT NOT NULL, accion TEXT NOT NULL
        );
    """)
    return conexion


def ejecutar_etl(datos_crudos, productos, referencia, conexion):
    datos = normalizar(datos_crudos)
    aceptadas, rechazadas, metricas, detalle = evaluar(datos, productos, referencia)
    lote = uuid4().hex
    estado = "PUBLICADO" if puerta_publicacion(len(datos), len(rechazadas)) else "BLOQUEADO"
    nuevas, existentes = 0, 0
    try:
        with conexion:
            if estado == "PUBLICADO":
                for producto in productos.itertuples(index=False):
                    existente = conexion.execute("SELECT producto FROM productos WHERE id_producto=?", (int(producto.id_producto),)).fetchone()
                    if existente is None:
                        conexion.execute("INSERT INTO productos VALUES (?, ?)", (int(producto.id_producto), producto.producto))
                    elif existente[0] != producto.producto:
                        raise ValueError("Cambio de maestro: requiere politica SCD aprobada")
                for venta in aceptadas.itertuples(index=False):
                    valores = (int(venta.id_producto), venta.fecha_venta.date().isoformat(), int(venta.monto_centavos), str(venta.moneda))
                    existente = conexion.execute("SELECT id_producto, fecha_venta, monto_centavos, moneda FROM ventas WHERE id_venta=?", (int(venta.id_venta),)).fetchone()
                    if existente is None:
                        conexion.execute("INSERT INTO ventas VALUES (?, ?, ?, ?, ?, ?, ?)", (int(venta.id_venta), *valores, venta.fila_fuente, lote))
                        nuevas += 1
                    elif existente == valores:
                        existentes += 1
                    else:
                        raise ValueError("Conflicto de contenido para una venta ya publicada")
                claves = [int(identificador) for identificador in aceptadas["id_venta"]]
                marcadores = ",".join("?" for _ in claves)
                destino = pd.read_sql_query(f"SELECT id_venta, moneda, monto_centavos FROM ventas WHERE id_venta IN ({marcadores})", conexion, params=claves)
                assert len(destino) == len(aceptadas)
                esperado = {str(moneda): int(total) for moneda, total in aceptadas.groupby("moneda")["monto_centavos"].sum().items()}
                obtenido = {str(moneda): int(total) for moneda, total in destino.groupby("moneda")["monto_centavos"].sum().items()}
                assert esperado == obtenido
            conexion.execute("INSERT INTO lotes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (lote, huella(datos_crudos), VERSION_CONTRATO, estado, len(datos), len(aceptadas), len(rechazadas), nuevas, existentes))
            conexion.executemany("INSERT INTO hallazgos VALUES (?, ?, ?, ?)", [(lote, fila.fila_fuente, fila.regla, fila.accion) for fila in detalle.itertuples(index=False)])
    except Exception:
        with conexion:
            conexion.execute("INSERT INTO lotes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (lote, huella(datos_crudos), VERSION_CONTRATO, "ERROR_TECNICO", len(datos), len(aceptadas), len(rechazadas), 0, 0))
        raise
    return {"lote": lote, "estado": estado, "nuevas": nuevas, "existentes": existentes, "aceptadas": aceptadas, "rechazadas": rechazadas, "metricas": metricas, "detalle": detalle}


def token_persona(valor, clave):
    if len(clave) < 32:
        raise ValueError("Usar una clave aleatoria de al menos 32 bytes para la demo")
    if pd.isna(valor) or not str(valor).strip():
        return None
    mensaje = f"demo:email:{str(valor).strip().lower()}".encode("utf-8")
    return hmac.new(clave, mensaje, hashlib.sha256).hexdigest()


def vista_por_rol(datos, rol, clave):
    columnas = ["id_venta", "id_producto", "fecha_venta", "monto_centavos", "moneda"]
    if rol == "analista":
        return datos[columnas].copy()
    if rol == "steward":
        resultado = datos[columnas].copy()
        resultado["email_token"] = datos["email"].map(lambda valor: token_persona(valor, clave))
        return resultado
    raise PermissionError("Rol sin vista autorizada en la simulacion")


def metadatos():
    return {
        "activo": "silver.ventas", "version": "1.0.0", "grano": "una fila por id_venta",
        "owner": "Gerencia Comercial", "steward": "Steward Comercial",
        "finalidad": "analitica de ventas", "clasificacion": "confidencial",
        "retencion": "por definir y aprobar antes de produccion",
        "columnas": [
            {"nombre": "id_venta", "tipo": "INTEGER", "nullable": False, "termino": "Identificador de venta", "origen": "origen.id_venta", "transformacion": "entero positivo", "reglas": ["DQ_ID", "DQ_UNICIDAD"]},
            {"nombre": "id_producto", "tipo": "INTEGER", "nullable": False, "termino": "Producto de la venta", "origen": "origen.id_producto", "transformacion": "lookup en productos", "reglas": ["DQ_FK_PRODUCTO"]},
            {"nombre": "fecha_venta", "tipo": "DATE", "nullable": False, "termino": "Fecha del evento", "origen": "origen.fecha_venta", "transformacion": "parseo ISO", "reglas": ["DQ_FECHA"]},
            {"nombre": "monto_centavos", "tipo": "INTEGER", "nullable": False, "termino": "Importe de linea en moneda original", "origen": "origen.monto", "transformacion": "Decimal por 100, sin conversion de moneda", "reglas": ["DQ_MONTO"]},
            {"nombre": "moneda", "tipo": "TEXT", "nullable": False, "termino": "Moneda original", "origen": "origen.moneda", "transformacion": "strip y upper", "reglas": ["DQ_MONEDA"]},
        ],
    }


def linaje(datos):
    return {
        "entidad_fuente": "ventas_ficticias", "huella": huella(datos),
        "actividad": "normalizar_validar_publicar", "agente": "servicio_etl_demo",
        "contrato": VERSION_CONTRATO, "entidad_destino": "silver.ventas",
        "campos": metadatos()["columnas"],
        "limite": "modelo didactico inspirado en PROV, no serializacion PROV conforme",
    }


def json_seguro(objeto):
    return json.dumps(objeto, ensure_ascii=True, indent=2, allow_nan=False)