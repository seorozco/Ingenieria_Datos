# Arquitectura Kimball · Etapa 1 — Planificación y Requerimientos del Proyecto

> **Arquitectura:** Kimball — Bottom-Up  
> **Posición en el ciclo:** Primera etapa. Define el alcance, el equipo y las necesidades de negocio antes de escribir una sola línea de SQL.

---

## El Ciclo de Vida Dimensional de Kimball

Ralph Kimball, en su obra *The Data Warehouse Lifecycle Toolkit*, describe un proceso sistemático llamado **Business Dimensional Lifecycle** para construir un sistema de Data Warehousing de forma exitosa. A diferencia de Inmon, que define primero toda la arquitectura empresarial antes de construir cualquier Data Mart, Kimball propone un ciclo iterativo orientado a entregar valor rápidamente en proyectos acotados.

El ciclo se estructura en tres pistas (tracks) paralelas que avanzan en conjunto:

```
INICIO DEL PROYECTO
        │
        ▼
┌───────────────────────────────┐
│  PLANIFICACIÓN DEL PROYECTO   │  ← Etapa 1
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│  DEFINICIÓN DE REQUERIMIENTOS │  ← Etapa 1 (continúa)
└──────┬───────┬────────────────┘
       │       │
       ▼       ▼
  PISTA DE  PISTA DE    PISTA DE
  DATOS     TECNOLOGÍA  BI/APLICACIONES
  (Etapas   (Etapas     (Etapa 5)
   2, 4)     3, 4)
       │       │               │
       └───────┴───────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  DESPLIEGUE    │  ← Etapa 5
              └────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ MANTENIMIENTO  │
              │ Y CRECIMIENTO  │
              └────────────────┘
```

---

## ¿Qué se construye en la Etapa 1?

La Etapa 1 establece los cimientos del proyecto antes de tocar datos, diseñar modelos o seleccionar herramientas. Responde cuatro preguntas fundamentales:

1. **¿Por qué?** — ¿Cuál es el problema de negocio que el DWH resolverá?
2. **¿Qué?** — ¿Qué procesos de negocio se incluyen en el alcance inicial?
3. **¿Para quién?** — ¿Quiénes son los usuarios y qué decisiones necesitan tomar?
4. **¿Cómo?** — ¿Con qué recursos, en qué plazos y bajo qué restricciones?

---

## 1. Planificación del Proyecto

### Justificación y caso de negocio

Antes de iniciar cualquier trabajo técnico, el proyecto debe tener una **justificación de negocio clara y cuantificable**. El equipo de datos debe poder responder:

- ¿Qué decisiones de negocio se toman hoy sin datos confiables?
- ¿Qué cuesta para la organización no tener esos datos? (tiempo, errores, oportunidades perdidas)
- ¿Cuánto valor generaría tenerlos? (en tiempo ahorrado, en mejores decisiones, en ingresos o costos)

**Ejemplo de justificación:**

> "El equipo de ventas dedica 3 horas semanales por vendedor reconciliando datos de 4 sistemas distintos para preparar su reporte de pipeline. Con 15 vendedores, eso es 45 horas semanales de trabajo de alto costo que podría eliminarse con un Data Mart de Ventas. Además, la dirección reporta que al menos 2 veces por mes se toman decisiones con datos inconsistentes entre los reportes del CRM y del ERP."

### El patrocinador ejecutivo (*Executive Sponsor*)

Todo proyecto de DWH exitoso tiene un **patrocinador ejecutivo**: un directivo con autoridad y presupuesto que cree en el proyecto y está dispuesto a defenderlo cuando surjan obstáculos organizacionales.

El patrocinador ejecutivo:
- Aprueba el presupuesto.
- Resuelve conflictos entre áreas.
- Garantiza la disponibilidad del tiempo de los usuarios de negocio para las entrevistas.
- Comunica el proyecto a la organización.

Sin un patrocinador ejecutivo comprometido, la probabilidad de fracaso del proyecto es muy alta.

### El equipo del proyecto

Un proyecto de Data Mart con la metodología Kimball requiere roles bien definidos:

| Rol | Responsabilidad |
|---|---|
| **Project Manager** | Coordina plazos, recursos, riesgos y comunicación. |
| **Arquitecto de Datos** | Diseña el modelo dimensional y la arquitectura técnica. |
| **Analista de Negocios** | Realiza las entrevistas, documenta requerimientos. |
| **Ingeniero ETL** | Diseña e implementa el proceso ETL. |
| **DBA / Ingeniero de Datos** | Diseña el esquema físico, optimiza performance. |
| **Desarrollador BI** | Construye los reportes y dashboards. |
| **Data Steward** | Garantiza la calidad y la semántica de los datos. |
| **Usuario Clave** | Experto de negocio que valida el modelo y los reportes. |

---

## 2. Definición de Requerimientos

### Las entrevistas de negocio

El proceso de entrevistas con los usuarios de negocio es el corazón de la Etapa 1. Kimball enfatiza que **el diseño del Data Mart debe surgir de las necesidades del negocio**, no de la estructura de los sistemas fuente.

**Objetivo de las entrevistas:** Entender qué preguntas necesita responder el negocio, qué decisiones toma, qué métricas son críticas y cuáles son los eventos de negocio que quieren analizar.

**Lo que NO se debe preguntar en las entrevistas:**
- ¿Qué tablas del sistema necesitan?
- ¿Qué reportes tienen ahora?
- ¿Qué formato quieren en el reporte?

**Lo que SÍ se debe preguntar:**
- ¿Cuáles son sus principales responsabilidades?
- ¿Qué decisiones críticas toma cada semana o mes?
- ¿Qué información necesita para tomar esas decisiones que hoy no tiene o tarda en obtener?
- ¿Cómo mide el éxito de su área?
- ¿Qué preguntas le hacen sus jefes o la dirección que usted no puede responder fácilmente?

### Guía de entrevista — Plantilla

```
ENTREVISTA DE REQUERIMIENTOS DE DATA WAREHOUSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fecha:          ___________________________
Entrevistado:   ___________________________
Cargo:          ___________________________
Área:           ___________________________
Entrevistador:  ___________________________

BLOQUE 1 — CONTEXTO
─────────────────────────────────────────────
1. ¿Cuál es su función principal en la organización?
2. ¿Cuáles son los 3 procesos de negocio más importantes de su área?
3. ¿Cómo mide actualmente el desempeño de esos procesos?

BLOQUE 2 — NECESIDADES DE INFORMACIÓN
─────────────────────────────────────────────
4. ¿Qué 3 preguntas sobre el negocio necesita responder con más frecuencia?
5. ¿Qué información necesita para tomar sus decisiones más importantes?
6. ¿Con qué frecuencia necesita esa información? (diario, semanal, mensual)
7. ¿Cuánto tiempo atrás necesita ver los datos? (30 días, 1 año, 5 años)

BLOQUE 3 — PROBLEMAS ACTUALES
─────────────────────────────────────────────
8. ¿Cómo obtiene esa información hoy? (sistema, Excel, manualmente)
9. ¿Cuánto tiempo le toma obtenerla?
10. ¿Con qué frecuencia los datos que recibe son incorrectos o inconsistentes?
11. ¿Hubo alguna decisión tomada con datos incorrectos que tuvo consecuencias?

BLOQUE 4 — VISIÓN DE FUTURO
─────────────────────────────────────────────
12. Si pudiera ver cualquier reporte con un click, ¿cuál sería?
13. ¿Qué análisis querría hacer que hoy no puede?
14. ¿Quién más en su equipo necesitaría acceso a esa información?

NOTAS ADICIONALES:
_______________________________________________
```

### Documentación de requerimientos

Los requerimientos capturados en las entrevistas se documentan en un formato estructurado. El documento de requerimientos es la **fuente de verdad** para el diseño del Data Mart.

**Ejemplo de documentación de un requerimiento:**

```
REQUERIMIENTO: REQ-VENTAS-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Título:         Análisis de ventas por vendedor y región

Solicitante:    Gerente de Ventas — Roberto Fernández
Prioridad:      Alta

Descripción:
   El Gerente de Ventas necesita comparar el rendimiento de cada
   vendedor contra su meta mensual, segmentado por región y
   categoría de producto, con vista histórica de 24 meses.

Preguntas que responde:
   - ¿Cuáles vendedores superaron su meta en el mes actual?
   - ¿Cuál es la tendencia de ventas de cada vendedor en los
     últimos 12 meses?
   - ¿Qué categorías de producto vende más cada vendedor?

Métricas requeridas:
   - Total de ventas ($ y unidades)
   - Meta del período ($ y unidades)
   - % de cumplimiento de meta
   - Margen bruto

Dimensiones requeridas:
   - Vendedor (nombre, zona, región)
   - Período (día, semana, mes, trimestre, año)
   - Producto (nombre, subcategoría, categoría)
   - Cliente (nombre, segmento)

Granularidad mínima:    Transacción / línea de pedido
Granularidad de análisis: Diaria (con posibilidad de drill-up a mensual)
Historial requerido:    24 meses hacia atrás
Frecuencia de actualización: Diaria (carga nocturna)
Usuarios:               Gerente de Ventas (1), Supervisores Regionales (4)
```

---

## 3. La Matriz de Procesos de Negocio (Bus Matrix)

Una de las herramientas más importantes de la metodología Kimball es la **Bus Matrix** (Matriz del Bus de Datos). Es un diagrama que cruza los **procesos de negocio** (filas) con las **dimensiones** que les aplican (columnas). La "X" indica que esa dimensión participa en ese proceso.

Esta matriz tiene dos propósitos fundamentales:
1. **Identificar el alcance inicial** del proyecto (qué procesos se incluyen en el primer Data Mart).
2. **Identificar las dimensiones conformadas**: dimensiones que aparecen en múltiples procesos y que deben ser diseñadas de forma consistente para permitir análisis cruzados.

**Ejemplo de Bus Matrix:**

```
                   │ Tiempo │ Cliente │ Producto │ Vendedor │ Proveedor │ Sucursal │ Canal │
───────────────────┼────────┼─────────┼──────────┼──────────┼───────────┼──────────┼───────┤
Ventas al cliente  │   X    │    X    │    X     │    X     │           │    X     │   X   │
Pedidos a proveed. │   X    │         │    X     │          │     X     │          │       │
Control inventario │   X    │         │    X     │          │           │    X     │       │
Gestión de RRHH    │   X    │         │          │    X     │           │    X     │       │
Finanzas/Contabilid│   X    │    X    │          │          │     X     │    X     │       │
───────────────────┴────────┴─────────┴──────────┴──────────┴───────────┴──────────┴───────┘

Las dimensiones que aparecen en múltiples filas son "dimensiones conformadas":
- Tiempo: aparece en TODOS los procesos → dimensión conformada universal
- Producto: aparece en 3 procesos → debe diseñarse de forma consistent
- Cliente: aparece en 2 procesos
- Sucursal: aparece en 4 procesos
```

---

## 4. Definición del alcance del primer Data Mart

Kimball recomienda iniciar con **un solo proceso de negocio** (una sola fila de la Bus Matrix) en el primer Data Mart. El criterio de selección debe ser:

- **Impacto de negocio:** ¿Qué proceso, si se analizara mejor, generaría más valor?
- **Disponibilidad de datos:** ¿Hay datos disponibles de calidad suficiente en los sistemas fuente?
- **Disposición del usuario:** ¿Hay usuarios comprometidos que participen activamente en el proyecto?
- **Complejidad técnica:** ¿La fuente de datos es abordable en el plazo del proyecto?

**Declaración de alcance — Ejemplo:**

```
ALCANCE DEL PRIMER DATA MART
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proceso de negocio:     Ventas al Cliente

EN ALCANCE:
  ✅ Análisis de ventas por vendedor, región, período
  ✅ Análisis de ventas por producto y categoría
  ✅ Análisis de ventas por canal (tienda física, e-commerce)
  ✅ Historial de 24 meses
  ✅ Actualización diaria (carga nocturna)
  ✅ Usuarios: Gerente de Ventas, 4 supervisores regionales, 2 analistas

FUERA DE ALCANCE (para futuras iteraciones):
  ❌ Análisis de rentabilidad por cliente (requiere datos de costos — Iteración 2)
  ❌ Predicción de ventas (requiere modelo de ML — Iteración 3)
  ❌ Análisis de pedidos a proveedores (proceso distinto — Iteración 2)
  ❌ Integración con datos de marketing (requerimiento en análisis — Iteración 2)

PLAZO ESTIMADO: 8 semanas
EQUIPO: 4 personas (1 arquitecto, 1 ETL, 1 DBA/BI, 1 analista)
```

---

## 5. Identificación de las Fuentes de Datos

Al finalizar la Etapa 1, el equipo ya sabe qué necesita medir. El paso siguiente es identificar **de dónde provienen esos datos**:

```
INVENTARIO DE FUENTES DE DATOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dato requerido     │ Sistema fuente │ Tipo    │ Calidad conocida
───────────────────┼────────────────┼─────────┼──────────────────
Transacciones      │ ERP (SAP)      │ SQL     │ Alta — sistema oficial
vendedor           │ CRM (Salesforce│ API     │ Media — sin validación
datos cliente      │ ERP (SAP)      │ SQL     │ Alta — master data
producto / catálog │ ERP (SAP)      │ SQL     │ Alta
metas por vendedor │ Excel (Planilla│ Archivo │ Baja — manual, sin control
región / zona      │ CRM            │ API     │ Media — cambia frecuente
```

Este inventario guía el diseño del ETL en la Etapa 4 y alerta sobre riesgos de calidad de datos que deben resolverse antes o durante el proyecto.

---

## Entregables de la Etapa 1

1. ✅ **Caso de negocio** con justificación y beneficios esperados del proyecto.
2. ✅ **Acta de constitución del proyecto** con alcance, recursos, plazos y sponsor.
3. ✅ **Notas de entrevistas** documentadas con todos los usuarios clave.
4. ✅ **Documento de Requerimientos** con todos los REQs numerados y priorizados.
5. ✅ **Bus Matrix** inicial con los procesos de negocio y sus dimensiones.
6. ✅ **Declaración de alcance** del primer Data Mart (en/fuera de alcance).
7. ✅ **Inventario de fuentes de datos** con sistemas, tipos y calidad preliminar.
8. ✅ **Glosario de negocio inicial** con definiciones acordadas de las métricas clave.

---

## Relación con la etapa siguiente

```
ETAPA 1: Planificación y Requerimientos
    Productos: Requerimientos, Bus Matrix, Alcance
        │
        ▼
ETAPA 2: Modelado Dimensional
    Usa los requerimientos para diseñar el esquema estrella:
    - ¿Qué proceso modelar? (Etapa 1 lo define)
    - ¿Qué granularidad? (Etapa 1 lo define)
    - ¿Qué dimensiones? (Bus Matrix lo indica)
    - ¿Qué métricas (hechos)? (Requerimientos lo definen)
        │
        ▼
ETAPA 3: Diseño Físico + ETAPA 4: Diseño ETL + ETAPA 5: BI y Despliegue
    (las tres pistas avanzan en paralelo desde aquí)
```

---

## 6. Evaluación de Riesgos del Proyecto

Un proyecto de Data Warehouse tiene riesgos específicos que deben identificarse tempranamente. Kimball recomienda realizar un análisis de riesgos en la Etapa 1 y revisarlo en cada iteración.

### Matriz de riesgos típica

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| El sponsor ejecutivo pierde interés o cambia de cargo | Media | Crítico | Tener un co-sponsor; demostrar resultados rápidos |
| Los datos fuente tienen peor calidad de la esperada | Alta | Alto | Evaluación temprana de calidad en la Etapa 1; plan de limpieza |
| Los usuarios no participan en las entrevistas | Media | Alto | Compromiso del sponsor; sesiones cortas y enfocadas |
| El ERP no tiene columna `updated_at` para extracción incremental | Media | Medio | Evaluar CDC (Debezium) o extracción completa con detección de cambios por hash |
| Cambio de prioridades del negocio a mitad del proyecto | Media | Alto | Alcance fijo para la iteración actual; cambios van a la siguiente iteración |
| El equipo no tiene experiencia en la herramienta de BI elegida | Baja | Medio | Capacitación al equipo en las primeras 2 semanas del proyecto |
| El volumen de datos supera la capacidad de la infraestructura | Baja | Alto | Sizing conservador + estrategia de escalamiento documentada |

### Factores críticos de éxito

Kimball identifica **10 factores críticos** que determinan el éxito o fracaso de un proyecto de DWH:

1. **Compromiso gerencial fuerte y sostenido** — sin sponsor, no hay proyecto.
2. **Caso de negocio convincente** — el proyecto debe generar valor medible.
3. **Relación fuerte entre IT y negocio** — las entrevistas son la evidencia de esta relación.
4. **Cultura analítica** — la organización debe estar dispuesta a tomar decisiones con datos.
5. **Alcance controlado** — no intentar resolver todo en la primera iteración.
6. **Arquitectura iterativa** — un Data Mart a la vez, conectados por dimensiones conformadas.
7. **Prototipos tempranos** — mostrar algo funcionando lo antes posible.
8. **Calidad de datos como prioridad** — datos incorrectos destruyen la confianza del usuario.
9. **Capacitación adecuada** — un sistema no usado es un fracaso.
10. **Soporte post-despliegue** — el sistema necesita mantenimiento y evolución continua.

---

## 7. Gestión del Cambio Organizacional

La construcción de un Data Warehouse no es solo un proyecto técnico: es un **cambio cultural**. Los usuarios pasan de tomar decisiones "por instinto" o con Excel a tomar decisiones basadas en datos integrados y confiables.

### Resistencia al cambio: fuentes comunes

| Fuente de resistencia | Manifestación | Cómo abordarla |
|---|---|---|
| **Miedo a perder control** | "Mi Excel funciona bien" | Mostrar que el DWH automatiza lo que hoy es manual |
| **Desconfianza en los datos** | "Esos números no pueden ser correctos" | Validar juntos los primeros reportes; transparentar las fórmulas |
| **Falta de tiempo** | "No tengo tiempo para entrevistas" | Sesiones cortas (45 min); el sponsor debe respaldar la prioridad |
| **Miedo al reemplazo** | "Si automatizan mis reportes, ¿para qué me necesitan?" | El DWH libera tiempo para análisis de mayor valor |

### Estrategia de adopción gradual

```
Fase 1 — "Quick Win" (semanas 1-2 post-despliegue)
  → Un solo dashboard que resuelve un dolor frecuente.
  → Usuarios piloto (3-5 personas) que validan y evangelizan.

Fase 2 — "Expansión controlada" (semanas 3-6)
  → Dar acceso a todos los usuarios del área.
  → Capacitación formal.
  → Retirar gradualmente los reportes manuales que el DWH reemplaza.

Fase 3 — "Estandarización" (meses 2-3)
  → Los reportes del DWH son la fuente oficial para reuniones de directorio.
  → Los reportes manuales ya no se generan.
  → Los usuarios piden nuevos análisis (señal de adopción exitosa).
```

---

## 8. Metodologías Ágiles aplicadas al DWH

Si bien Kimball no formuló su metodología usando terminología ágil (su obra principal es de 1998-2008), su enfoque iterativo es altamente compatible con Scrum o Kanban:

### Adaptación a Scrum

| Concepto Kimball | Equivalente Scrum |
|---|---|
| Iteración (1 Data Mart) | Épica |
| Entrevistas de requerimientos | Refinamiento del backlog |
| Diseño del modelo dimensional | Sprint 1-2 |
| ETL + carga inicial | Sprint 2-4 |
| Dashboards + validación | Sprint 4-5 |
| Despliegue + capacitación | Sprint 5-6 (Release) |

### User Stories para un proyecto de DWH

```
COMO Gerente de Ventas
QUIERO ver las ventas del mes actual por vendedor comparadas con su meta
PARA identificar quién necesita soporte y quién merece reconocimiento

Criterios de aceptación:
  - El dashboard muestra ventas reales vs. meta para cada vendedor.
  - Los datos se actualizan diariamente antes de las 07:00 AM.
  - Puedo filtrar por región.
  - Los números coinciden exactamente con el reporte manual de Excel.
```

```
COMO Analista Comercial
QUIERO poder analizar las ventas por cualquier combinación de producto, región y período
PARA identificar patrones y oportunidades que no son visibles en los reportes estándar

Criterios de aceptación:
  - Puedo arrastrar libremente dimensiones y métricas en un análisis ad-hoc.
  - El historial disponible es de al menos 24 meses.
  - Las consultas responden en menos de 10 segundos.
```

---

## Lecturas recomendadas

- **Kimball, R. & Ross, M.** — *The Data Warehouse Lifecycle Toolkit*, 2da edición. Capítulo 1: "Introduction to the Kimball Lifecycle". Wiley.
- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit*, 3ra edición. Capítulo 1: "Data Warehousing, Business Intelligence and Dimensional Modeling Primer". Wiley.
- **Hoberman, S.** — *Data Modeling Made Simple*. Technics Publications.
- **PMI** — *A Guide to the Project Management Body of Knowledge (PMBOK Guide)*, 7ma edición. (Para las prácticas de gestión del proyecto).
- **Kotter, J.P.** — *Leading Change*. Harvard Business Review Press. (Para gestión del cambio organizacional).
- **Schwaber, K. & Sutherland, J.** — *The Scrum Guide*. (Para la adaptación ágil del ciclo de vida Kimball).
