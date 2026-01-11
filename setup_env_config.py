#!/usr/bin/env python
"""
Script para configurar PYTHON_ENV.md en nuevos proyectos.

Uso:
    python setup_env_config.py --project "MiProyecto" --path "D:/mi_proyecto"
"""

import argparse
from pathlib import Path
from datetime import datetime


TEMPLATE = """# Python Environment Configuration

**IMPORTANTE:** Este proyecto usa un entorno virtual compartido centralizado.

## Entorno Virtual

**Ubicación del entorno virtual:**
```
D:\\gestoria_agentes\\.venv
```

**Gestor de paquetes:** `uv`

**Proyecto actual:** `{project_name}` (ubicado en `{project_path}`)

---

## 🚀 Ejecución Rápida

### Para Claude Code y Asistentes IA

**Ejecutar Python en este proyecto:**

```bash
# Formato general
/d/gestoria_agentes/.venv/Scripts/python.exe [script.py] [argumentos]

# Ejemplo concreto para este proyecto
cd {project_path_unix}
/d/gestoria_agentes/.venv/Scripts/python.exe main.py
```

**Instalar dependencias faltantes:**

```bash
cd D:/gestoria_agentes
uv pip install [nombre-paquete]
```

---

## 📋 Comandos Esenciales

### Ejecutar Scripts Python

```bash
# Desde cualquier ubicación
/d/gestoria_agentes/.venv/Scripts/python.exe {project_path_unix}/script.py

# O cambiar al directorio primero
cd {project_path_unix}
/d/gestoria_agentes/.venv/Scripts/python.exe script.py
```

### Ejecutar Código Python Inline

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe -c "import sys; print(sys.version)"
```

### Instalar Paquetes

```bash
cd D:/gestoria_agentes
uv pip install paquete1 paquete2 paquete3
```

### Instalar desde requirements.txt

```bash
cd D:/gestoria_agentes
uv pip install -r {project_path_unix}/requirements.txt
```

### Listar Paquetes Instalados

```bash
cd D:/gestoria_agentes
uv pip list
```

---

## ✅ Reglas de Oro

### ✅ HACER

- ✅ Usar siempre `/d/gestoria_agentes/.venv/Scripts/python.exe`
- ✅ Instalar paquetes con `uv` desde `D:/gestoria_agentes`
- ✅ Verificar paquetes instalados antes de instalar nuevos
- ✅ Mantener `requirements.txt` actualizado

### ❌ NO HACER

- ❌ Usar `python` directamente (usa el Python del sistema)
- ❌ Usar `pip install` (usa `uv pip install`)
- ❌ Crear un nuevo `.venv` en este proyecto
- ❌ Instalar paquetes sin verificar si ya están

---

## 🔍 Verificación del Entorno

### Verificar Python Correcto

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe -c "import sys; print(sys.executable)"
```

**Salida esperada:**
```
D:\\gestoria_agentes\\.venv\\Scripts\\python.exe
```

---

## 📦 Gestión de Dependencias

### Workflow Recomendado

1. **Verificar si el paquete ya está instalado:**
   ```bash
   cd D:/gestoria_agentes
   uv pip list | grep nombre-paquete
   ```

2. **Si NO está instalado, instalarlo:**
   ```bash
   cd D:/gestoria_agentes
   uv pip install nombre-paquete
   ```

3. **Actualizar requirements.txt:**
   Añadir manualmente a `requirements.txt`

---

## 🤖 Nota para Claude Code / IA Assistants

**Cuando trabajes en este proyecto:**

1. **SIEMPRE** lee este archivo primero para entender la configuración del entorno
2. **NUNCA** uses `python` sin la ruta completa
3. **VERIFICA** paquetes instalados con `uv pip list` antes de instalar
4. **USA** `/d/gestoria_agentes/.venv/Scripts/python.exe` para todos los comandos Python
5. **INSTALA** paquetes con `cd D:/gestoria_agentes && uv pip install paquete`

**Ejemplo de comando correcto:**
```bash
cd {project_path_unix}
/d/gestoria_agentes/.venv/Scripts/python.exe main.py
```

---

## 📄 Metadata

- **Entorno Virtual:** D:\\gestoria_agentes\\.venv
- **Gestor:** uv
- **Python Version:** 3.11.12
- **Proyecto:** {project_name}
- **Ruta:** {project_path}
- **Última actualización:** {update_date}

---

## 🔗 Referencias

- [Documentación de uv](https://github.com/astral-sh/uv)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
"""


def create_env_config(project_name: str, project_path: str, output_file: str = None):
    """
    Crea el archivo PYTHON_ENV.md para un proyecto.

    Args:
        project_name: Nombre del proyecto
        project_path: Ruta del proyecto (ej: D:/mi_proyecto)
        output_file: Ruta donde guardar el archivo (default: {project_path}/PYTHON_ENV.md)
    """
    # Convertir path a formato Unix (para bash)
    project_path_unix = project_path.replace("\\", "/")
    if project_path_unix.startswith("D:"):
        project_path_unix = "/d" + project_path_unix[2:]

    # Fecha actual
    update_date = datetime.now().strftime("%Y-%m-%d")

    # Rellenar plantilla
    content = TEMPLATE.format(
        project_name=project_name,
        project_path=project_path,
        project_path_unix=project_path_unix,
        update_date=update_date
    )

    # Determinar ruta de salida
    if output_file is None:
        output_path = Path(project_path) / "PYTHON_ENV.md"
    else:
        output_path = Path(output_file)

    # Crear directorio si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Escribir archivo
    output_path.write_text(content, encoding="utf-8")

    print(f"✅ Archivo creado: {output_path}")
    print(f"📦 Proyecto: {project_name}")
    print(f"📁 Ruta: {project_path}")
    print(f"\n💡 Siguiente paso:")
    print(f"   Copia este archivo a tu repositorio y actualiza .gitignore")


def main():
    parser = argparse.ArgumentParser(
        description="Configurar PYTHON_ENV.md para nuevos proyectos"
    )
    parser.add_argument(
        "--project",
        "-p",
        required=True,
        help="Nombre del proyecto (ej: 'MiProyecto')"
    )
    parser.add_argument(
        "--path",
        "-d",
        required=True,
        help="Ruta del proyecto (ej: 'D:/mi_proyecto')"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Ruta de salida personalizada (opcional)"
    )

    args = parser.parse_args()

    create_env_config(args.project, args.path, args.output)


if __name__ == "__main__":
    main()
