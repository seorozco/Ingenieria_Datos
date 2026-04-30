# Guía de Instalación: Python, VS Code y Entornos Virtuales

Esta guía detalla los pasos para configurar un ambiente de desarrollo profesional en Python desde cero.

---

## 1. Instalación de Python
El primer paso es instalar el intérprete de Python en tu sistema.

1.  **Descarga:** Ve a [python.org/downloads](https://python.org) y descarga la última versión estable.
2.  **Instalación en Windows:**
    *   Ejecuta el instalador.
    *   **IMPORTANTE:** Marca la casilla **"Add Python to PATH"** antes de dar clic en *Install Now*. Esto permite usar Python desde cualquier terminal.
3.  **Verificación:** Abre una terminal (CMD o PowerShell) y escribe:
    ```bash
    python --version
    ```

---

## 2. Configuración de Visual Studio Code
VS Code es el editor más popular para Python por su versatilidad.

1.  **Descarga:** Instálalo desde [://visualstudio.com](https://://visualstudio.com/).
2.  **Extensión de Python:** 
    *   Abre VS Code.
    *   Ve al icono de **Extensions** (o presiona `Ctrl + Shift + X`).
    *   Busca e instala la extensión llamada **"Python"** (publicada por Microsoft).

---

## 3. Manejo de Entornos Virtuales (`venv`)
El entorno virtual aísla las librerías de tu proyecto para evitar conflictos de versiones.

1.  **Abrir Proyecto:** Abre VS Code y selecciona `File > Open Folder...` para elegir la carpeta de tu proyecto.
2.  **Crear Entorno:** Abre la terminal integrada de VS Code (`Ctrl + ñ` o `` Ctrl + ` ``) y ejecuta:
    ```bash
    python -m venv .venv
    ```
3.  **Activar Entorno:**
    *   **Windows:** `.venv\Scripts\activate`
    *   **Mac/Linux:** `source .venv/bin/activate`
    * *Nota: Verás el nombre `(.venv)` al inicio de tu línea de comandos cuando esté activo.*
4.  **Vincular a VS Code:** Presiona `Ctrl + Shift + P`, escribe `Python: Select Interpreter` y selecciona la opción que dice `('.venv': venv)`.

---

## 4. Instalación de Librerías con `pip`
`pip` es el gestor de paquetes de Python. Una vez que tu entorno virtual esté **activo**, puedes instalar librerías.

### Comandos básicos:
*   **Instalar una librería:**
    ```bash
    pip install nombre_de_la_libreria
    # Ejemplo: pip install pandas
    ```
*   **Ver librerías instaladas:**
    ```bash
    pip list
    ```
*   **Crear archivo de requerimientos:** (Útil para compartir tu proyecto)
    ```bash
    pip freeze > requirements.txt
    ```
*   **Instalar todo desde un archivo:**
    ```bash
    pip install -r requirements.txt
    ```

---
**¡Listo!** Ya tienes un entorno limpio y profesional para empezar a programar.
