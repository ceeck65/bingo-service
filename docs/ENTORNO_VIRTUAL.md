# 🐍 Entorno Virtual - Microservicio de Bingo

## ¿Qué es un Entorno Virtual?

Un entorno virtual es un directorio aislado que contiene una instalación específica de Python y sus paquetes. Esto permite:

- ✅ Aislar las dependencias del proyecto
- ✅ Evitar conflictos entre diferentes proyectos
- ✅ Mantener versiones específicas de paquetes
- ✅ Facilitar el despliegue y distribución

## 🚀 Configuración Rápida

### Opción 1: Script Automático (Recomendado)

```bash
# Navegar al proyecto
cd /home/ceeck65/Projects/bingo_service

# Ejecutar configuración automática
./setup.sh

# Activar entorno
source venv/bin/activate
```

### Opción 2: Manual

```bash
# Navegar al proyecto
cd /home/ceeck65/Projects/bingo_service

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate
```

## 📋 Comandos Útiles

### Activación y Desactivación

```bash
# Activar entorno virtual
source venv/bin/activate

# Desactivar entorno virtual
deactivate

# Verificar que está activado (debería mostrar la ruta del venv)
which python
```

### Gestión de Dependencias

```bash
# Ver paquetes instalados
pip list

# Instalar dependencias del proyecto
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Actualizar requirements.txt
pip freeze > requirements.txt
```

### Comandos del Proyecto

```bash
# Iniciar servidor de desarrollo
python manage.py runserver

# Aplicar migraciones
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Ejecutar demos
python demo.py
python demo_winner.py

# Ejecutar pruebas
python test_bingo.py
```

## 📁 Estructura del Entorno Virtual

```
venv/
├── bin/                    # Ejecutables
│   ├── activate           # Script de activación
│   ├── python            # Interprete Python
│   └── pip               # Gestor de paquetes
├── lib/                   # Bibliotecas Python
│   └── python3.13/
│       └── site-packages/ # Paquetes instalados
└── include/               # Headers de desarrollo
```

## 🔧 Scripts de Automatización

### activate.sh
Script que activa el entorno virtual y muestra información útil:

```bash
./activate.sh
```

### setup.sh
Script que configura todo el entorno desde cero:

```bash
./setup.sh
```

## 📦 Archivos de Dependencias

### requirements.txt
Dependencias principales del proyecto:
- Django 5.2.7
- Django REST Framework 3.16.1
- Django CORS Headers 4.6.0

### requirements-dev.txt
Dependencias para desarrollo:
- pytest (testing)
- black (formateo de código)
- flake8 (linting)
- requests (pruebas de API)

## 🚨 Solución de Problemas

### Problema: "python: command not found"
```bash
# Verificar que Python 3 está instalado
python3 --version

# Si no está instalado, instalarlo
sudo dnf install python3 python3-pip
```

### Problema: "pip: command not found"
```bash
# Instalar pip
sudo dnf install python3-pip
```

### Problema: "Permission denied" en scripts
```bash
# Hacer scripts ejecutables
chmod +x setup.sh activate.sh
```

### Problema: Dependencias no se instalan
```bash
# Actualizar pip
pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 🔄 Flujo de Trabajo Recomendado

1. **Activar entorno virtual**:
   ```bash
   source venv/bin/activate
   ```

2. **Desarrollar/Probar**:
   ```bash
   python manage.py runserver
   python demo.py
   ```

3. **Instalar nuevas dependencias**:
   ```bash
   pip install nueva-dependencia
   pip freeze > requirements.txt
   ```

4. **Desactivar entorno**:
   ```bash
   deactivate
   ```

## 📝 Notas Importantes

- ✅ **Siempre activar el entorno** antes de trabajar en el proyecto
- ✅ **Commitear requirements.txt** para mantener dependencias sincronizadas
- ✅ **No commitear venv/** (está en .gitignore)
- ✅ **Usar scripts de automatización** para configuraciones repetitivas

## 🎯 Beneficios del Entorno Virtual

1. **Aislamiento**: Cada proyecto tiene sus propias dependencias
2. **Versionado**: Control específico de versiones de paquetes
3. **Portabilidad**: Fácil configuración en diferentes máquinas
4. **Limpieza**: No contamina el Python del sistema
5. **Colaboración**: requirements.txt garantiza consistencia entre desarrolladores

¡El entorno virtual hace que el desarrollo sea más profesional y confiable! 🚀
