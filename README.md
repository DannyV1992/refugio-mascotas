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
│ └── workflows/
│   └── deploy.yml # CI/CD GitHub Actions
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
│   ├── contacto.html # Colaboración y contacto
│   └── app.js # Lógica frontend
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🚀 Instalación y ejecución

### **Opción 1: Con Docker (recomendado)**

Clona el repositorio
```
git clone [tu-repositorio-url]
cd refugio-mascotas
```

Levanta toda la aplicación con Docker
```
docker-compose up --build
```

Accede a los servicios:
Frontend: http://localhost:8080
Backend API: http://localhost:8001
Documentación API: http://localhost:8001/docs


### **Opción 2: Instalación manual**

#### **1. Base de datos**

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
Renombra .env.example por .env y agrega tus credenciales de MySQL
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

## 🐳 DevOps y despliegue

### **Docker**
- **Dockerfile**: containeriza el backend FastAPI
- **docker-compose.yml**: orquesta backend, frontend (Nginx) y base de datos MySQL
- **Volumes**: persistencia de datos de MySQL y uploads
- **Networks**: comunicación interna entre contenedores

### **CI/CD con GitHub Actions**
- **Pruebas automáticas**: validación de imports y dependencias
- **Build testing**: construcción y prueba de contenedores Docker
- **Deploy ready**: preparado para despliegue en Digital Ocean
- **Trigger**: se ejecuta automáticamente en cada push a `main`

### **Seguridad**
- **Sanitización XSS**: limpieza automática de inputs maliciosos
- **Validación de datos**: teléfonos, emails, rangos de edad
- **Manejo de archivos**: validación de tipos y tamaños de imagen
- **Variables de entorno**: credenciales protegidas

---

## 💡 Personalización y extensión

- Todos los formularios, modelos y rutas son extensibles
- Lista de colaboradores, estadísticas de donaciones y más: fácil de expandir
- Tabla de solicitudes/adopciones/registro de histórico integrados

---

## 👩‍💻 Tecnologías utilizadas

### **Backend**
- **FastAPI**: Framework web moderno y rápido
- **MySQL**: Base de datos relacional robusta
- **Pydantic**: Validación y serialización de datos
- **Uvicorn**: Servidor ASGI para producción

### **Frontend**
- **HTML5 semántico**: Estructura moderna
- **Tailwind CSS**: Framework utility-first para diseño
- **JavaScript ES6+**: Interactividad y llamadas a API
- **Fetch API**: Comunicación asíncrona con backend

### **DevOps**
- **Docker**: Containerización y portabilidad
- **GitHub Actions**: CI/CD automatizado
- **Nginx**: Servidor web para frontend en producción

### **Procesamiento de datos**
- **Pandas**: Análisis y limpieza de datos
- **Dog CEO API/Cat Facts API**: Datos externos curiosos

---

## 📧 Autores

- Daniel Vásquez González
- Susana Herrera Fonseca
- Kendra Gutiérrez Vega

---
