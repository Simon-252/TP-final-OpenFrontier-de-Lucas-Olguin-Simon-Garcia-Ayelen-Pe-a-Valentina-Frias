# OpenFrontier: Monitoreo del Paso Cristo Redentor

## 📝 Descripción del Proyecto
INTEGRANTES: Lucas Olguin - Simon Garcia - Ayelen Peña - Valentina Frias
OpenFrontier es una aplicación web desarrollada con el framework *Flask* de Python, diseñada para proporcionar información en tiempo real sobre el estado (Abierto/Cerrado) y las condiciones climáticas del *Paso Cristo Redentor*.

El proyecto utiliza:
* *SQLAlchemy* y *MySQL* para la persistencia de datos.
* *Flask-Migrate* para gestionar las migraciones de la base de datos.
* *Web Scraping* (con Beautiful Soup) para obtener el estado oficial del paso de una fuente externa.
* *APIs externas* (OpenWeatherMap) para obtener datos climáticos precisos.
* *Flask-APScheduler* para automatizar la actualización periódica del estado del paso y el clima.
* *JWT* para un sistema de autenticación con roles (user y admin).

## 🧱 Entidades Principales del Modelo de Datos

El sistema se basa en tres entidades principales:

| Entidad | Descripción | Campos Clave |
| :--- | :--- | :--- |
| *User* | Usuarios del sistema. Permite iniciar sesión y asigna roles (user o admin) para acceso a rutas protegidas. | username, email, password (hasheada), role. |
| *Paso* | Almacena el estado operativo actual del Paso (ej: "Abierto", "Cerrado", "Habilitado"), la hora de la última actualización y la fuente. Se actualiza mediante Web Scraping. | nombre (único, ej: "Cristo Redentor"), estado, actualizado. |
| *Clima* | Registra las condiciones meteorológicas del Paso. Está vinculado a una instancia de Paso. Se actualiza automáticamente desde una API externa. | temperatura, descripcion, viento, fecha. |

*

## ⚙️ Instrucciones de Instalación y Ejecución

Sigue estos pasos para configurar y levantar el servidor de la aplicación.

### 1. Requisitos Previos

Tener instalado:
* *Python 3.x*
* Un servidor de base de datos *MySQL* en ejecución.

### 2. Configuración del Entorno

*a. Entorno Virtual*

Crea y activa un entorno virtual:

```bash
### Crear entorno
python -m venv .venv

# Activar entorno (Windows)
.\.venv\Scripts\actívate

###Instalación de Dependencias

pip install -r requirements.txt

###Fragmento de código y configuracion del .env
# Configuración de la Base de Datos MySQL
MYSQL_USER=root
MYSQL_PASSWORD=TuContraseñaDeMySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB_NAME=base_openfrontier # Asegúrate de que esta DB exista o créala

SECRET_KEY=UnaClaveMuySecretaParaJWT
WEATHER_API_KEY=Tu_Clave_De_OpenWeatherMap

###Base de Datos y Seeding
El proyecto utiliza Flask-Migrate para la estructura de la base de datos y un script de seeding para cargar usuarios iniciales (incluidos en users.json).

a. Correr Migraciones

Ejecuta el siguiente comando para aplicar las migraciones y crear las tablas (users, pasos, climas) en tu base de datos MySQL:

Bash
flask db upgrade

###Cargar Usuarios Iniciales (Seeding)

Bash

python seed.py

###Para levantar servidor:

python app.py
