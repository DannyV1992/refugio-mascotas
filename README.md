# Refugio de Mascotas 🐾

Proyecto full‑stack para administración, adopción y colaboración en un refugio de mascotas. Incluye:
- Backend API con **FastAPI** y **MySQL**
- Frontend HTML+JS estilizado con **Tailwind CSS**
- Pipeline de limpieza y backups en Python
- Soporte para imágenes, voluntariado, apadrinamiento, donaciones, difusión y adopción

---

## 🌟 Características principales

- **Gestión de mascotas**: agrega, edita, elimina y lista mascotas (con foto, datos, contacto, estado).
- **Catálogo de mascotas**: carta digital para público interesado en adoptar.
- **Solicitud de adopción robusta**: formulario dedicado, validación completa.
- **Ingreso de mascotas**: página especial, soporte imagen y mucho detalle.
- **Colaboración**: registros para ser voluntario, apadrinar, donar o difundir.
- **Subida de imágenes**: drag&drop y preview.
- **API de datos curiosos**: integra Cat Facts y Dog CEO.
- **Pipeline de limpieza**: respaldo de datos y control de calidad con pandas.
- **Paleta y UI unificadas**: experiencia visual moderna y consistente.

## 📁 Estructura del proyecto
```
refugio-mascotas/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   ├── uploads/ # Carpeta para imágenes
│   └── .env (usar .env.example y renombrarlo)
├── pipeline/
│   ├── flows.py
│   ├── reports/
|   ├── logs/
│   └── backups/
├── sql/
│   └── init.sql
├── frontend/
│   ├── index.html # Página Home
│   ├── mascotas.html # Registrar mascotas
│   ├── adopciones.html # Solicitar adopción
│   ├── contacto.html # Colabora & contacto
│   └── app.js # Lógica frontend
└── README.md
```

## 🚀 Instalación rápida

#### **1. Base de Datos**

- Debes tener instalado **MySQL 8.x**
- Ejecuta el script para crear y poblar la base:

```
mysql -u root -p < sql/init.sql
```

#### **2. Backend (FastAPI)**

```
cd backend
```
Prepara entorno virtual
```
python -m venv venv
source venv/bin/activate # En Windows: venv\Scripts\activate
```
Instala dependencias
```
pip install -r requirements.txt
```
Renombra .env.example a .env y agrega tus credenciales de MySQL
```
cp .env.example .env
```

- ***Levanta el servidor***:
```
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### **3. Frontend**

- Sin necesidad de frameworks. Solo abre los archivos HTML desde `/frontend`
- Si usas fetch, sirve como sitio estático (por ejemplo: Live Server de VSCode, Python http.server, etc.)

```
cd frontend
python -m http.server 8080
```
o usa cualquier servidor estático a tu preferencia

---

## 🔗 Endpoints principales API (FastAPI)

- `GET /mascotas` – Lista mascotas del refugio
- `POST /mascotas` – Agrega mascota (formulario ingresar)
- `POST /upload-image` – Sube imagen y retorna URL
- `GET /api/external-pet-data` – API pública, datos curiosos (razas/curiosidad gatos)
- `POST /solicitudes-adopcion` – Solicita adoptar
- `POST /solicitudes-voluntariado` – Conviértete en voluntario
- `POST /donaciones` – Registra donación
- `POST /apadrinamientos` – Apadrina mascota
- `POST /colaboradores-difusion` – Ofrece ayuda a difundir/refugio

---

## 🖼️ Imágenes y archivos

- Las imágenes se guardan en `/backend/uploads/`
- Al crear/editar mascota, primero sube la imagen con `/upload-image` y usa la URL resultante

---

## 🤖 Pipeline de datos

Pipeline automatizado para limpieza, análisis y respaldo de datos del refugio.

### ✨ Características del pipeline

- **Limpieza de datos**: Valida y normaliza información de mascotas
- **Análisis de tendencias**: Genera insights sobre adopciones y popularidad
- **Backups automáticos**: Respaldos organizados por fecha de todas las tablas
- **Reportes diarios**: Estadísticas y alertas del refugio
- **Sistema de alertas**: Notifica sobre solicitudes pendientes y datos incompletos

### 🚀 Ejecución

#### Ejecución manual

```
cd pipeline
python flows.py
```

#### Ejecución programada (automática)

```
cd pipeline
python flows.py --schedule
```
Se ejecuta diariamente a las 2:00 AM

### 📁 Archivos generados

- **`backups/`**: Respaldos CSV organizados por fecha
- **`reports/`**: Reportes diarios en JSON con estadísticas y alertas
- **`logs/`**: Logs de ejecución con métricas de calidad

### 📊 Reportes incluyen

- Total de mascotas y disponibilidad
- Solicitudes de adopción pendientes
- Voluntarios activos y donaciones mensuales
- Especies más populares y tendencias de adopción
- Alertas automáticas (solicitudes viejas, mascotas sin foto, donaciones pendientes)

---

## 💡 Personalización y extensión

- Todos los formularios, modelos y rutas son extensibles
- Lista de colaboradores, estadísticas de donaciones y más: fácil de expandir
- Tabla de solicitudes/adopciones/registro de histórico integrados

---

## 👩‍💻 Créditos y frameworks

- **Tailwind CSS**: CSS framework utility-first
- **FastAPI**: API en Python super rápida
- **MySQL**: Base de datos robusta
- **Pandas**: Procesamiento de datos para backups/logs
- **Dog CEO API/Cat Facts API**: Para datos curiosos

---

## 📧 Autores

- Daniel Vásquez González
- Susana Herrera Fonseca
- Kendra Gutiérrez Vega
---
