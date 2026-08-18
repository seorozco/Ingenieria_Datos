# Unidad IV · Guia de Tablas de Hechos
## Como disenar y cargar una tabla de hechos de calidad (caso `dw.fact_ventas`)

---

## 1. Que es una tabla de hechos

Una tabla de hechos guarda eventos medibles del negocio.

En este caso, el evento es:

- una linea de factura de venta.

Por eso, cada fila de `dw.fact_ventas` representa una unica linea de una factura.

Idea clave:

- Las dimensiones explican el contexto (quien, que, donde, cuando).
- La fact guarda los numeros que queremos analizar (cuanto, margen, cantidad).

---

## 2. Primera decision critica: definir el grano

En modelado dimensional, el grano es la decision mas importante.

Grano elegido en la notebook:

- **1 fila = 1 linea por detalle de factura**.

Esto permite responder preguntas como:

- Cuanto vendimos por mes, cliente y categoria.
- Que vendedor tiene mejor ticket promedio.
- Que productos pierden margen por descuentos.

Si el grano se define mal, todo lo demas se vuelve confuso.

Regla docente:

- Antes de crear columnas, escribir una frase de grano en una sola linea.

---

## 3. Estructura de la fact del caso

La tabla `dw.fact_ventas` combina:

1. Claves foraneas a dimensiones (FK)
2. Llave de negocio para evitar duplicados
3. Medidas numericas
4. Metadato de carga

### 3.1 Claves foraneas

- `id_tiempo`
- `id_cliente_sk`
- `id_producto_sk`
- `id_vendedor_sk`
- `id_ciudad_sk`

Estas claves conectan la fact con el contexto analitico.

### 3.2 Llave de negocio operacional

- `numero_factura`
- `numero_linea`

Se usa una restriccion unica para impedir duplicados del mismo evento.

### 3.3 Medidas

- `cantidad`
- `precio_unitario`
- `monto_neto`
- `monto_impuesto`
- `costo_estimado`
- `margen_bruto`

### 3.4 Auditoria

- `fecha_carga`

Permite saber cuando fue insertada la fila en el DW.

---

## 4. DDL recomendado (patron base)

```sql
CREATE TABLE dw.fact_ventas (
    id_fact_venta_sk      BIGINT IDENTITY(1,1) PRIMARY KEY,
    id_tiempo             INT           NOT NULL,
    id_cliente_sk         INT           NOT NULL,
    id_producto_sk        INT           NOT NULL,
    id_vendedor_sk        INT           NOT NULL,
    id_ciudad_sk          INT           NOT NULL,
    numero_factura        INT           NOT NULL,
    numero_linea          INT           NOT NULL,
    cantidad              DECIMAL(18,4) NOT NULL,
    precio_unitario       DECIMAL(18,4) NOT NULL,
    monto_neto            DECIMAL(18,2) NOT NULL,
    monto_impuesto        DECIMAL(18,2) NULL,
    costo_estimado        DECIMAL(18,2) NULL,
    margen_bruto          DECIMAL(18,2) NULL,
    fecha_carga           DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_fact_ventas_doc_linea UNIQUE (numero_factura, numero_linea)
);
```

Punto didactico:

- La PK surrogate (`id_fact_venta_sk`) da estabilidad tecnica.
- La llave unica operacional protege el grano de negocio.

---

## 5. Flujo ETL aplicado en la notebook

## Paso 1: Extraccion desde origen transaccional

Se leen lineas de `Sales.InvoiceLines`, unidas con facturas y clientes.

Transformaciones iniciales:

- Convertir fecha a datetime.
- Derivar `id_tiempo` con formato `YYYYMMDD`.
- Ordenar por factura + linea origen.
- Generar `numero_linea` deterministico.
- Calcular `costo_estimado = monto_neto - margen_bruto`.

## Paso 2: Resolucion de NK -> SK

### SCD2 (cliente y producto)

Se busca la fila de dimension vigente segun `fecha_factura`.

Si no hay match por rango, se usa fallback a `es_actual = 1`.

Esto evita perder filas por huecos de vigencia.

### SCD1 (vendedor y ciudad)

Mapeo directo por natural key.

### Tiempo

Match directo por `id_tiempo`.

## Paso 3: Rechazo de filas sin SK valida

Filas con FK nula se separan en `rechazos_sk`.

Solo se cargan las filas de `df_fact_ok`.

## Paso 4: Carga incremental idempotente

Se compara (`numero_factura`, `numero_linea`) contra lo ya cargado.

- Si no existe: insertar.
- Si ya existe: no insertar.

Resultado:

- El proceso se puede re-ejecutar sin duplicar historico.

---

## 6. Reglas de calidad minimas para tablas de hechos

La notebook valida cinco controles clave.

### 6.1 Volumen origen vs destino

Compara cantidad de filas extraidas vs cargadas.

### 6.2 Integridad referencial

Verifica FK huerfanas en cada dimension.

Esperado: todos los contadores en cero.

### 6.3 Duplicados de negocio

Busca repetidos en (`numero_factura`, `numero_linea`).

Esperado: cero duplicados.

### 6.4 Reglas de negocio numericas

- `cantidad > 0`
- `precio_unitario >= 0`
- `monto_neto >= 0`

### 6.5 Reconciliacion mensual

Compara suma mensual de `monto_neto` entre origen y DW.

Si la diferencia es cercana a cero, la carga esta reconciliada.

---

## 7. Como conectar la fact con preguntas de negocio

Una fact bien diseniada se evalua por su capacidad de respuesta.

Consultas trabajadas en la notebook:

1. Ventas por mes, categoria y cliente.
2. Clientes con mayor margen.
3. Evolucion de ventas por ciudad y estado.
4. Vendedor con mejor ticket promedio.
5. Productos con perdida de margen por descuentos frecuentes.

Regla de oro de modelado:

- Si una pregunta prioritaria no se puede responder con claridad, el diseno aun no esta terminado.

---

## 8. Errores frecuentes en estudiantes (y como evitarlos)

1. Definir mal el grano.
- Sintoma: medidas duplicadas o inconsistentes.
- Prevencion: escribir y validar la frase de grano antes del DDL.

2. Mezclar NK con SK durante joins.
- Sintoma: FK huerfanas o explosion de filas.
- Prevencion: estandarizar nombres (`*_nk`, `*_sk`) y revisar cada merge.

3. Ignorar vigencias SCD2.
- Sintoma: cliente/producto historico mal asignado.
- Prevencion: resolver por rango temporal usando fecha del hecho.

4. No implementar incremental idempotente.
- Sintoma: duplicados en recargas.
- Prevencion: constraint unica + filtro de nuevas filas.

5. Omitir controles post-carga.
- Sintoma: errores silenciosos en dashboards.
- Prevencion: checklist obligatorio al final de cada corrida.

---

## 9. Checklist docente para evaluar una fact

```text
[ ] El grano esta definido en una frase precisa.
[ ] Hay una PK surrogate tecnica.
[ ] Las FK a dimensiones estan completas y sin huerfanas.
[ ] Existe llave de negocio unica para evitar duplicados.
[ ] Las medidas tienen tipo de dato correcto (precision y escala).
[ ] Hay estrategia incremental idempotente.
[ ] Se ejecutan controles de calidad y reconciliacion.
[ ] La fact responde las preguntas de negocio prioritarias.
```

---

## 10. Mini practica sugerida para estudiantes

1. Tomar la consulta de ventas por mes y agregar filtro por `pais`.
2. Crear una variante de ticket promedio por cliente.
3. Detectar top 10 productos con menor margen porcentual.
4. Explicar si el problema es de precio, costo o descuento.

Objetivo pedagogico:

- Pasar de "cargar datos" a "interpretar comportamiento del negocio".

---

## 11. Conclusiones

Una tabla de hechos de calidad no es solo una tabla grande.

Es una pieza de diseno que debe:

- respetar el grano,
- mantener integridad con dimensiones,
- cargarse de forma repetible,
- y responder preguntas reales del negocio.

El caso `dw.fact_ventas` muestra un flujo completo y reusable para futuros hechos transaccionales.