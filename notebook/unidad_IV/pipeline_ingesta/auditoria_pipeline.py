import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

_AUDITORIA_ACTIVA = None


SQL_AUDITORIA = """
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'auditoria')
    EXEC('CREATE SCHEMA auditoria');
IF OBJECT_ID('auditoria.ejecuciones_etapa', 'U') IS NULL
BEGIN
    CREATE TABLE auditoria.ejecuciones_etapa (
        id_ejecucion NVARCHAR(36) PRIMARY KEY,
        etapa NVARCHAR(60) NOT NULL,
        tabla NVARCHAR(100) NULL,
        estado NVARCHAR(20) NOT NULL,
        inicio DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        fin DATETIME2(7) NULL,
        entradas BIGINT NULL,
        salidas BIGINT NULL,
        relaciones BIGINT NULL,
        detalle_json NVARCHAR(MAX) NULL
    );
END;
IF OBJECT_ID('auditoria.linaje_registros', 'U') IS NULL
BEGIN
    CREATE TABLE auditoria.linaje_registros (
        id_ejecucion NVARCHAR(36) NOT NULL,
        tabla_origen NVARCHAR(100) NOT NULL,
        clave_origen NVARCHAR(100) NOT NULL,
        tabla_destino NVARCHAR(100) NOT NULL,
        clave_destino NVARCHAR(100) NOT NULL,
        detalle_json NVARCHAR(MAX) NOT NULL,
        FOREIGN KEY (id_ejecucion) REFERENCES auditoria.ejecuciones_etapa(id_ejecucion),
        PRIMARY KEY (id_ejecucion, tabla_origen, clave_origen, tabla_destino, clave_destino)
    );
END;
"""


def relacion(origen, clave_origen, destino, clave_destino, **detalle):
    return {
        'tabla_origen': origen,
        'clave_origen': str(clave_origen),
        'tabla_destino': destino,
        'clave_destino': str(clave_destino),
        'detalle_json': json.dumps(detalle, ensure_ascii=True, default=str)
    }


def guardar_relaciones(conn, id_ejecucion, relaciones):
    cantidad = 0
    bloque = []
    for registro in relaciones:
        bloque.append(dict(registro, id_ejecucion=id_ejecucion))
        if len(bloque) == 1000:
            pd.DataFrame(bloque).to_sql(
                'linaje_registros', conn, schema='auditoria',
                if_exists='append', index=False, chunksize=500
            )
            cantidad += len(bloque)
            bloque = []
    if bloque:
        pd.DataFrame(bloque).to_sql(
            'linaje_registros', conn, schema='auditoria',
            if_exists='append', index=False, chunksize=500
        )
        cantidad += len(bloque)
    return cantidad


def verificar_cobertura(conn, linaje, hechos):
    ultimas = pd.read_sql_query('''
        SELECT etapa, tabla, estado FROM (
            SELECT etapa, tabla, estado, ROW_NUMBER() OVER (
                PARTITION BY etapa, COALESCE(tabla, '') ORDER BY inicio DESC, id_ejecucion DESC
            ) AS orden
            FROM auditoria.ejecuciones_etapa
        ) ejecuciones WHERE orden = 1
    ''', conn)
    estados = {(fila.etapa, None if pd.isna(fila.tabla) else fila.tabla): fila.estado
               for fila in ultimas.itertuples(index=False)}
    esperadas = [(etapa, tabla) for etapa in
                 ['01_raw', '02_profiling', '03_cuarentena', '04_staging']
                 for tabla in ['invoice_lines', 'invoices']]
    esperadas += [('05_dimensiones', None), ('06_hechos', None)]
    etapas_faltantes = [f'{etapa}/{tabla or "pipeline"}' for etapa, tabla in esperadas
                       if estados.get((etapa, tabla)) != 'OK']
    observadas = pd.read_sql_query('''
        SELECT DISTINCT l.tabla_destino, l.clave_destino
        FROM auditoria.linaje_registros l
        JOIN auditoria.ejecuciones_etapa e ON e.id_ejecucion = l.id_ejecucion
        WHERE e.estado = 'OK'
    ''', conn)
    registradas = set(zip(observadas['tabla_destino'], observadas['clave_destino']))
    necesarias = set()
    for fila in linaje.itertuples(index=False):
        for tabla, clave in [('invoice_lines', fila.id_raw_linea), ('invoices', fila.id_raw_factura)]:
            necesarias.add((f'raw.{tabla}', str(int(clave))))
            necesarias.add((f'calidad:{tabla}', str(int(clave))))
            necesarias.add((f'staging.{tabla}', str(int(clave))))
        necesarias.add(('dw.fact_ventas', str(int(fila.id_fact_venta_sk))))
    for fila in hechos.itertuples(index=False):
        for dimension, clave in [('dim_tiempo', 'id_tiempo'), ('dim_cliente', 'id_cliente_sk'),
                                 ('dim_producto', 'id_producto_sk'), ('dim_vendedor', 'id_vendedor_sk'),
                                 ('dim_ciudad', 'id_ciudad_sk')]:
            if pd.notna(getattr(fila, clave)):
                necesarias.add((f'dw.{dimension}', str(int(getattr(fila, clave)))))
    faltantes = necesarias - registradas
    return not etapas_faltantes and not faltantes, {
        'etapas_sin_auditoria_ok': etapas_faltantes,
        'puntos_de_linaje_sin_registro': len(faltantes)
    }


class AuditoriaEtapa:
    def __init__(self, engine, etapa, tabla=None, directorio_logs=None):
        self.engine = engine
        self.etapa = etapa
        self.tabla = tabla
        self.id_ejecucion = str(uuid.uuid4())
        self.estado = 'EN_CURSO'
        self.ipython = None
        logs = Path(directorio_logs or Path(__file__).parent / 'logs')
        logs.mkdir(parents=True, exist_ok=True)
        self.archivo_log = logs / f'{etapa}_{tabla or "pipeline"}_{self.id_ejecucion}.jsonl'
        self.logger = logging.getLogger(f'auditoria.{self.id_ejecucion}')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.handler = logging.FileHandler(self.archivo_log, encoding='utf-8')
        self.handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(self.handler)
        self._log('INICIO')
        try:
            if self.engine is None:
                if __package__:
                    from .conexion_sqlserver import obtener_engines
                else:
                    from conexion_sqlserver import obtener_engines
                _, self.engine = obtener_engines()
            with self.engine.begin() as conn:
                conn.execute(text(SQL_AUDITORIA))
                conn.execute(text('''
                    INSERT INTO auditoria.ejecuciones_etapa
                        (id_ejecucion, etapa, tabla, estado)
                    VALUES (:id, :etapa, :tabla, 'EN_CURSO')
                '''), {'id': self.id_ejecucion, 'etapa': etapa, 'tabla': tabla})
        except Exception as error:
            self.estado = 'ERROR'
            self._log('ERROR_INICIO', tipo_error=type(error).__name__)
            self._cerrar()
            raise

    def _log(self, evento, **detalle):
        self.logger.info(json.dumps({
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'id_ejecucion': self.id_ejecucion, 'etapa': self.etapa,
            'tabla': self.tabla, 'evento': evento, **detalle
        }, ensure_ascii=True, default=str))

    def vigilar_kernel(self):
        try:
            from IPython import get_ipython
            self.ipython = get_ipython()
        except ImportError:
            return
        if self.ipython is not None:
            self.ipython.events.register('post_run_cell', self._error_celda)

    def _error_celda(self, resultado):
        error = resultado.error_before_exec or resultado.error_in_exec
        if error is not None and self.estado == 'EN_CURSO':
            self.registrar_error(error)

    def _cerrar(self):
        if self.ipython is not None:
            self.ipython.events.unregister('post_run_cell', self._error_celda)
            self.ipython = None
        self.handler.close()
        self.logger.removeHandler(self.handler)

    def registrar_error(self, error):
        if self.estado != 'EN_CURSO':
            return
        self.estado = 'ERROR'
        detalle = {'tipo_error': type(error).__name__}
        self._log('ERROR', **detalle)
        try:
            with self.engine.begin() as conn:
                conn.execute(text('''
                    UPDATE auditoria.ejecuciones_etapa
                    SET estado = 'ERROR', fin = SYSUTCDATETIME(), detalle_json = :detalle
                    WHERE id_ejecucion = :id
                '''), {'id': self.id_ejecucion, 'detalle': json.dumps(detalle)})
        except Exception as fallo_auditoria:
            self._log('ERROR_REGISTRO_SQL', tipo_error=type(fallo_auditoria).__name__)
        finally:
            self._cerrar()

    def finalizar(self, contexto):
        if self.estado != 'EN_CURSO':
            raise RuntimeError('La etapa no esta en curso; volver a ejecutar desde el inicio')
        try:
            with self.engine.begin() as conn:
                entradas, salidas, relaciones, detalle = self._resultado(conn, contexto)
                cantidad = guardar_relaciones(conn, self.id_ejecucion, relaciones)
                conn.execute(text('''
                    UPDATE auditoria.ejecuciones_etapa
                    SET estado = 'OK', fin = SYSUTCDATETIME(), entradas = :entradas,
                        salidas = :salidas, relaciones = :relaciones, detalle_json = :detalle
                    WHERE id_ejecucion = :id
                '''), {
                    'id': self.id_ejecucion, 'entradas': entradas, 'salidas': salidas,
                    'relaciones': cantidad, 'detalle': json.dumps(detalle, default=str)
                })
            self.estado = 'OK'
            self._log('FIN', entradas=entradas, salidas=salidas, relaciones=cantidad, **detalle)
            print(f'[OK] Auditoria {self.id_ejecucion}: {cantidad} relaciones de linaje')
            print(f'Log: {self.archivo_log}')
            self._cerrar()
        except Exception as error:
            self.registrar_error(error)
            raise

    def _resultado(self, conn, contexto):
        tabla = self.tabla
        if self.etapa == '00_gobierno':
            mapa = contexto['mapa']
            relaciones = (
                relacion(fila.origen, '*', 'catalogo:mapa', f'{fila.origen}->{fila.destino}',
                         destino_declarado=fila.destino, aporte=fila.aporte, nivel='METADATOS')
                for fila in mapa.itertuples(index=False)
            )
            return len(mapa), len(mapa), relaciones, {'nivel': 'METADATOS', 'no_es_carga_de_datos': True}

        if self.etapa == '01_raw':
            original = contexto.get('df_origen')
            lote = contexto.get('LOTE_ID')
            if original is None or lote is None:
                raise ValueError('No se extrajeron datos RAW')
            datos = pd.read_sql_query(text(f'''
                SELECT id_raw, lote_id, payload, hash_sha256 FROM raw.{tabla}
                WHERE lote_id = :lote
            '''), conn, params={'lote': lote})
            if len(datos) != len(original):
                raise ValueError('El lote RAW no coincide con los registros extraidos')
            clave = 'InvoiceLineID' if tabla == 'invoice_lines' else 'InvoiceID'
            origen = 'Sales.InvoiceLines' if tabla == 'invoice_lines' else 'Sales.Invoices'
            relaciones = (
                relacion(origen, json.loads(fila.payload)[clave], f'raw.{tabla}', fila.id_raw,
                         lote=fila.lote_id, hash_sha256=fila.hash_sha256)
                for fila in datos.itertuples(index=False)
            )
            return len(original), len(datos), relaciones, {'lote': lote}

        if self.etapa == '02_profiling':
            datos = contexto.get('df_raw')
            if datos is None:
                raise ValueError('No se leyeron datos para profiling')
            errores = contexto.get('errores_validacion', [])
            motivos = {}
            for error in errores:
                clave = (int(error['id_raw']), error['lote_id'])
                motivos.setdefault(clave, []).append({
                    'tipo_error': error['tipo_error'], 'campo': error['campo_afectado'],
                    'es_critico': int(error['es_critico'])
                })
            validacion = 'validacion_calidad' if tabla == 'invoice_lines' else 'validacion_calidad_invoices'
            guardados = pd.read_sql_query(f'''
                SELECT id_validacion, id_raw, lote_id, tipo_error, campo_afectado
                FROM raw.{validacion}
            ''', conn)
            esperados = {(int(error['id_raw']), error['lote_id'], error['tipo_error'],
                          error['campo_afectado']) for error in errores}
            presentes = {(int(fila.id_raw), fila.lote_id, fila.tipo_error, fila.campo_afectado)
                         for fila in guardados.itertuples(index=False)}
            if not esperados.issubset(presentes):
                raise ValueError('Hay incidencias de calidad no persistidas en SQL')

            def relaciones_calidad():
                for fila in datos.itertuples(index=False):
                    yield relacion(f'raw.{tabla}', fila.id_raw, f'calidad:{tabla}', fila.id_raw,
                                   lote=fila.lote_id,
                                   errores=motivos.get((int(fila.id_raw), fila.lote_id), []),
                                   estado='RECHAZADO' if any(error['es_critico'] for error in
                                       motivos.get((int(fila.id_raw), fila.lote_id), [])) else 'ACEPTADO')
                for fila in guardados.itertuples(index=False):
                    if (int(fila.id_raw), fila.lote_id, fila.tipo_error, fila.campo_afectado) in esperados:
                        yield relacion(f'raw.{tabla}', fila.id_raw, f'raw.{validacion}',
                                       fila.id_validacion, lote=fila.lote_id, tipo_error=fila.tipo_error)
            return len(datos), len(datos), relaciones_calidad(), {'incidencias': len(errores)}

        if self.etapa == '03_cuarentena':
            datos = pd.read_sql_query(f'''
                SELECT id_quarantine, id_raw, lote_id, estado FROM quarantine.{tabla}
            ''', conn)
            relaciones = (
                relacion(f'raw.{tabla}', fila.id_raw, f'quarantine.{tabla}', fila.id_quarantine,
                         lote=fila.lote_id, estado=fila.estado)
                for fila in datos.itertuples(index=False)
            )
            criticos = contexto.get('df_criticos')
            if criticos is None:
                raise ValueError('No se identificaron los registros criticos')
            faltantes = set(zip(criticos['id_raw'], criticos['lote_id'])) - set(zip(datos['id_raw'], datos['lote_id']))
            if faltantes:
                raise ValueError('Hay registros criticos no persistidos en cuarentena')
            return len(criticos), len(datos), relaciones, {'alcance': 'cuarentena_observada'}

        if self.etapa == '04_staging':
            clave = 'id_linea' if tabla == 'invoice_lines' else 'id_raw'
            validacion = 'validacion_calidad' if tabla == 'invoice_lines' else 'validacion_calidad_invoices'
            datos = pd.read_sql_query(f'''
                SELECT s.{clave} AS clave_destino, r.id_raw, r.lote_id, r.hash_sha256
                FROM staging.{tabla} s JOIN raw.{tabla} r ON r.id_raw = s.{clave}
            ''', conn)
            rechazados = conn.execute(text(f'''
                SELECT COUNT(*) FROM staging.{tabla} s JOIN raw.{tabla} r ON r.id_raw = s.{clave}
                WHERE EXISTS (SELECT 1 FROM quarantine.{tabla} q
                    WHERE q.id_raw = r.id_raw AND q.lote_id = r.lote_id)
                OR EXISTS (SELECT 1 FROM raw.{validacion} v
                    WHERE v.id_raw = r.id_raw AND v.lote_id = r.lote_id AND v.es_critico = 1)
            ''')).scalar_one()
            if rechazados:
                raise ValueError('Staging contiene registros rechazados')
            relaciones = (
                relacion(f'raw.{tabla}', fila.id_raw, f'staging.{tabla}', fila.clave_destino,
                         lote=fila.lote_id, hash_sha256=fila.hash_sha256)
                for fila in datos.itertuples(index=False)
            )
            return len(contexto['df_raw']), len(datos), relaciones, {'rechazados_en_staging': 0}

        if self.etapa == '05_dimensiones':
            dimensiones = [
                ('dim_tiempo', 'calendario:fecha', 'fecha', 'id_tiempo'),
                ('dim_cliente', 'Sales.Customers', 'id_cliente_nk', 'id_cliente_sk'),
                ('dim_producto', 'Warehouse.StockItems', 'id_producto_nk', 'id_producto_sk'),
                ('dim_vendedor', 'Application.People', 'id_vendedor_nk', 'id_vendedor_sk'),
                ('dim_ciudad', 'Application.Cities', 'id_ciudad_nk', 'id_ciudad_sk')
            ]
            observadas = [(dimension, origen, natural, sustituta, pd.read_sql_query(
                f'SELECT {natural}, {sustituta} FROM dw.{dimension}', conn
            )) for dimension, origen, natural, sustituta in dimensiones]

            def relaciones_dimensiones():
                for dimension, origen, natural, sustituta, datos in observadas:
                    for fila in datos.to_dict('records'):
                        yield relacion(origen, fila[natural], f'dw.{dimension}', fila[sustituta],
                                       tipo_clave='NK->SK')
            cantidad = sum(len(item[4]) for item in observadas)
            return cantidad, cantidad, relaciones_dimensiones(), {'alcance': 'versiones_dimensionales_observadas'}

        if self.etapa == '06_hechos':
            return self._hechos(conn, contexto)

        if self.etapa == '07_publicacion':
            linaje = contexto['linaje_publicado']
            publicacion = contexto['ID_PUBLICACION']
            relaciones = (
                relacion('dw.fact_ventas', fila.id_fact_venta_sk, 'dw.fact_ventas_publicadas',
                         fila.id_fact_venta_sk, id_publicacion=publicacion)
                for fila in linaje.itertuples(index=False)
            )
            return len(linaje), len(linaje), relaciones, {'id_publicacion': publicacion}

        if self.etapa == '08_reporte':
            datos = contexto['reporte_ventas']
            archivo = contexto['archivo_reporte']
            relaciones = (
                relacion('dw.fact_ventas_publicadas', fila.id_fact_venta_sk,
                         'archivo:reporte_integral', fila.id_fact_venta_sk, archivo=str(archivo))
                for fila in datos.itertuples(index=False)
            )
            return len(datos), len(datos), relaciones, {'archivo': str(archivo)}
        raise ValueError(f'Etapa no reconocida: {self.etapa}')

    def _hechos(self, conn, contexto):
        candidatos = contexto['df_fact_ok']
        ventas = contexto['ventas']
        hechos = pd.read_sql_query('SELECT * FROM dw.fact_ventas', conn)
        hechos = hechos.merge(candidatos[['numero_factura', 'numero_linea']],
                              on=['numero_factura', 'numero_linea'], validate='one_to_one')
        fuentes = ventas[['numero_factura', 'numero_linea', 'id_raw_linea']]
        hechos = hechos.merge(fuentes, on=['numero_factura', 'numero_linea'], validate='one_to_one')
        cabeceras = pd.read_sql_query('''
            SELECT id_raw, id_factura FROM (
                SELECT s.id_raw, s.id_factura, ROW_NUMBER() OVER (
                    PARTITION BY s.id_factura ORDER BY s.ultima_edicion DESC, s.id_raw DESC
                ) AS version_cabecera
                FROM staging.invoices s
                JOIN raw.invoices r ON r.id_raw = s.id_raw AND r.lote_id = s.lote_id
                WHERE NOT EXISTS (SELECT 1 FROM quarantine.invoices q
                    WHERE q.id_raw = r.id_raw AND q.lote_id = r.lote_id)
                AND NOT EXISTS (SELECT 1 FROM raw.validacion_calidad_invoices v
                    WHERE v.id_raw = r.id_raw AND v.lote_id = r.lote_id AND v.es_critico = 1)
            ) versiones WHERE version_cabecera = 1
        ''', conn)
        hechos = hechos.merge(cabeceras, left_on='numero_factura', right_on='id_factura',
                              validate='many_to_one')
        if len(hechos) != len(candidatos):
            raise ValueError('No se puede vincular cada hecho con sus dos registros de staging')

        def relaciones_hechos():
            for fila in hechos.itertuples(index=False):
                yield relacion('staging.invoice_lines', fila.id_raw_linea,
                               'dw.fact_ventas', fila.id_fact_venta_sk)
                yield relacion('staging.invoices', fila.id_raw,
                               'dw.fact_ventas', fila.id_fact_venta_sk)
                for dimension, clave in [
                    ('dim_tiempo', 'id_tiempo'), ('dim_cliente', 'id_cliente_sk'),
                    ('dim_producto', 'id_producto_sk'), ('dim_vendedor', 'id_vendedor_sk'),
                    ('dim_ciudad', 'id_ciudad_sk')
                ]:
                    yield relacion(f'dw.{dimension}', getattr(fila, clave),
                                   'dw.fact_ventas', fila.id_fact_venta_sk)
        return len(ventas), len(hechos), relaciones_hechos(), {
            'fallback_scd2': contexto.get('usos_version_actual', {}),
            'rechazos_sk': len(contexto.get('rechazos_sk', [])),
            'rechazos_cabecera': len(contexto.get('rechazos_cabecera', []))
        }


def iniciar_etapa(etapa, tabla=None):
    global _AUDITORIA_ACTIVA
    import sys
    carpeta = str(Path(__file__).resolve().parent)
    if carpeta not in sys.path:
        sys.path.insert(0, carpeta)
    if _AUDITORIA_ACTIVA is not None and _AUDITORIA_ACTIVA.estado == 'EN_CURSO':
        _AUDITORIA_ACTIVA.registrar_error(RuntimeError('Etapa anterior interrumpida'))
    auditoria = AuditoriaEtapa(None, etapa, tabla)
    _AUDITORIA_ACTIVA = auditoria
    auditoria.vigilar_kernel()
    return auditoria