DROP SCHEMA IF EXISTS refugio_mascotas;
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS refugio_mascotas;
USE refugio_mascotas;

-- Tabla principal de mascotas
CREATE TABLE IF NOT EXISTS mascotas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especie ENUM('perro', 'gato', 'otro') NOT NULL,
    edad INT DEFAULT NULL,
    descripcion TEXT,
    imagen_url VARCHAR(500) DEFAULT NULL,
    tamano ENUM('pequeno', 'mediano', 'grande') DEFAULT NULL,
    genero ENUM('macho', 'hembra') DEFAULT NULL,
    contacto_nombre VARCHAR(100) DEFAULT NULL,
    contacto_telefono VARCHAR(20) DEFAULT NULL,
    estado ENUM('disponible', 'adoptado') DEFAULT 'disponible',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de datos limpios del pipeline
CREATE TABLE IF NOT EXISTS mascotas_cleaned (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mascota_id INT NOT NULL,
    data_quality_score DECIMAL(3,2) DEFAULT 1.00,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id) ON DELETE CASCADE
);

-- Nueva tabla para solicitudes de adopción
CREATE TABLE IF NOT EXISTS solicitudes_adopcion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mascota_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    tipo_vivienda ENUM('casa', 'apartamento', 'casa_jardin') NOT NULL,
    otras_mascotas ENUM('no', 'perros', 'gatos', 'ambos', 'otros') NOT NULL,
    experiencia ENUM('primera_vez', 'poca', 'moderada', 'mucha') NOT NULL,
    motivacion TEXT NOT NULL,
    horas_disponibles ENUM('1-3', '4-6', '6-8', '8+', 'todo_dia') NOT NULL,
    presupuesto VARCHAR(20) NOT NULL,
    estado ENUM('pendiente', 'revisando', 'aprobada', 'rechazada') DEFAULT 'pendiente',
    notas_admin TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id) ON DELETE CASCADE
);

-- Tabla para solicitudes de voluntariado
CREATE TABLE IF NOT EXISTS solicitudes_voluntariado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    areas TEXT NOT NULL,
    disponibilidad ENUM('mañanas', 'tardes', 'fines_semana', 'flexible') NOT NULL,
    experiencia TEXT DEFAULT NULL,
    estado ENUM('pendiente', 'revisando', 'aprobado', 'rechazado') DEFAULT 'pendiente',
    notas_admin TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla para donaciones
CREATE TABLE IF NOT EXISTS donaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_donacion ENUM('monetaria', 'especie') NOT NULL,
    monto DECIMAL(10,2) DEFAULT NULL,
    descripcion_especie TEXT DEFAULT NULL,
    nombre_donante VARCHAR(100) NOT NULL,
    telefono_donante VARCHAR(20) NOT NULL,
    email_donante VARCHAR(100) DEFAULT NULL,
    estado ENUM('pendiente', 'confirmada', 'recibida') DEFAULT 'pendiente',
    fecha_recepcion DATE DEFAULT NULL,
    notas_admin TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla para apadrinamiento
CREATE TABLE IF NOT EXISTS apadrinamientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_padrino VARCHAR(100) NOT NULL,
    telefono_padrino VARCHAR(20) NOT NULL,
    email_padrino VARCHAR(100) NOT NULL,
    preferencia_especie ENUM('perro', 'gato', 'mayor', 'especiales', '') DEFAULT '',
    aportacion_mensual DECIMAL(8,2) NOT NULL,
    mascota_asignada_id INT DEFAULT NULL,
    estado ENUM('pendiente', 'activo', 'pausado', 'cancelado') DEFAULT 'pendiente',
    fecha_inicio DATE DEFAULT NULL,
    notas_admin TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mascota_asignada_id) REFERENCES mascotas(id) ON DELETE SET NULL
);

-- Tabla para colaboradores de difusión
CREATE TABLE IF NOT EXISTS colaboradores_difusion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    tipos_difusion TEXT NOT NULL,
    redes_sociales TEXT DEFAULT NULL,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Mascotas disponibles
INSERT INTO mascotas (nombre, especie, edad, descripcion, imagen_url, tamaño, genero, contacto_nombre, contacto_telefono, estado) VALUES
('Max', 'perro', 3, 'Perro muy amigable y juguetón. Le encanta correr en el parque y jugar con niños.', '/uploads/max.jpg', 'mediano', 'macho', 'Ana González', '+506 8888 1122', 'disponible'),
('Luna', 'gato', 2, 'Gata tranquila y cariñosa. Perfecta para apartamentos, muy independiente.', '/uploads/luna.jpg', 'pequeno', 'hembra', 'Javier Ramírez', '+506 8765 4321', 'disponible'),
('Rocky', 'perro', 5, 'Perro guardián muy leal. Necesita espacio para correr y una familia activa.', '/uploads/rocky.jpg', 'grande', 'macho', 'Equipo del Refugio', '+506 2244 5566', 'disponible'),
('Mia', 'gato', 1, 'Gatita muy activa y curiosa. Le gusta jugar con pelotas y trepar.', '/uploads/mia.jpg', 'pequeno', 'hembra', 'Equipo del Refugio', '+506 2244 5566', 'adoptado'),
('Buddy', 'perro', 7, 'Perro mayor, muy tranquilo y obediente. Ideal para personas mayores.', '/uploads/buddy.jpg', 'mediano', 'macho', 'Luis Fernández', '+506 8567 2345', 'disponible'),
('Whiskers', 'gato', 4, 'Gato muy sociable, le encanta la compañía humana. Perfecto para familias.', '/uploads/whiskers.jpg', 'mediano', 'macho', 'Equipo del Refugio', '+506 2244 5566', 'disponible'),
('Bella', 'perro', 2, 'Perra muy energética y cariñosa. Le encanta jugar y pasear.', '/uploads/bella.jpg', 'pequeno', 'hembra', 'Iván Ureña', '+506 6001 2233', 'disponible');

-- Solicitudes de adopción ejemplo
INSERT INTO solicitudes_adopcion (mascota_id, nombre, telefono, email, direccion, tipo_vivienda, otras_mascotas, experiencia, motivacion, horas_disponibles, presupuesto, estado) VALUES
(1, 'Laura Campos', '+506 8700 1122', 'laura.campos@correo.cr', 'Del ICE 100 metros norte, San José', 'casa_jardin', 'no', 'moderada', 'Toby sería perfecto para mi familia, tenemos espacio y tiempo para él.', '6-8', '1000-3000', 'pendiente'),
(2, 'José Murillo', '+506 7000 2233', 'jose.murillo@correo.cr', 'Frente a la Plaza de Deportes, Cartago', 'apartamento', 'no', 'poca', 'Deseo compañía felina tranquila y Nina es ideal.', '4-6', '1000-3000', 'revisando'),
(5, 'Ana Solano', '+506 6001 3344', 'ana.solano@correo.cr', 'De la iglesia 200 este, Heredia', 'casa', 'gatos', 'mucha', 'Tengo experiencia cuidando perros mayores como Tina.', 'todo_dia', '3000-7000', 'aprobada');

-- Solicitudes de voluntariado (Costa Rica)
INSERT INTO solicitudes_voluntariado (nombre, telefono, email, areas, disponibilidad, experiencia) VALUES
('Patricia Castro', '+506 8777 8888', 'patricia.castro@correo.cr', '["cuidado_directo", "limpieza"]', 'mañanas', 'He colaborado en refugios en el GAM.'),
('Miguel Mora', '+506 8999 0000', 'miguel.mora@correo.cr', '["eventos", "redes"]', 'fines_semana', 'Trabajo en comunicación y eventos de bienestar animal.');

-- Donaciones (Costa Rica)
INSERT INTO donaciones (tipo_donacion, monto, nombre_donante, telefono_donante, email_donante, estado) VALUES
('monetaria', 20000.00, 'Gabriela Guevara', '+506 9000 1234', 'gabriela.guevara@correo.cr', 'confirmada'),
('especie', NULL, 'Federico Ruiz', '+506 9100 2233', 'federico.ruiz@correo.cr', 'pendiente');

UPDATE donaciones SET descripcion_especie = '30 kg de alimento para perro, mantas y collares' WHERE id = 2;

-- Apadrinamientos (Costa Rica)
INSERT INTO apadrinamientos (nombre_padrino, telefono_padrino, email_padrino, preferencia_especie, aportacion_mensual, estado) VALUES
('Lucía Fernández', '+506 9222 2333', 'lucia.fernandez@correo.cr', 'gato', 8000.00, 'pendiente'),
('Rafael Gómez', '+506 9333 2444', 'rafael.gomez@correo.cr', 'mayor', 12000.00, 'activo');

-- Difusión (Costa Rica)
INSERT INTO colaboradores_difusion (nombre, email, tipos_difusion, redes_sociales) VALUES
('Sandra Ramírez', 'sandra.ramirez@correo.cr', '["redes_sociales","volantes"]', 'Instagram @sandra_rcr'),
('Pedro Salazar', 'pedro.salazar@correo.cr', '["fotografia","charlas"]', 'Facebook @pedrosalazar, TikTok @salazarfotos');

-- Índices para rendimiento (se mantienen igual)
CREATE INDEX idx_mascotas_especie ON mascotas(especie);
CREATE INDEX idx_mascotas_estado ON mascotas(estado);
CREATE INDEX idx_mascotas_created_at ON mascotas(created_at);
CREATE INDEX idx_mascotas_tamaño ON mascotas(tamaño);
CREATE INDEX idx_mascotas_genero ON mascotas(genero);

CREATE INDEX idx_solicitudes_mascota_id ON solicitudes_adopcion(mascota_id);
CREATE INDEX idx_solicitudes_estado ON solicitudes_adopcion(estado);
CREATE INDEX idx_solicitudes_created_at ON solicitudes_adopcion(created_at);
CREATE INDEX idx_solicitudes_email ON solicitudes_adopcion(email);

CREATE INDEX idx_voluntariado_estado ON solicitudes_voluntariado(estado);
CREATE INDEX idx_voluntariado_email ON solicitudes_voluntariado(email);
CREATE INDEX idx_donaciones_tipo ON donaciones(tipo_donacion);
CREATE INDEX idx_donaciones_estado ON donaciones(estado);
CREATE INDEX idx_apadrinamientos_estado ON apadrinamientos(estado);
CREATE INDEX idx_difusion_estado ON colaboradores_difusion(estado);