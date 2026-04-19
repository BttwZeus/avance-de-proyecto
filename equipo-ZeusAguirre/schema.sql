-- Sistema de Reservas para Espacios de Trabajo
-- Dominio 1 - TechNova Solutions

CREATE DATABASE IF NOT EXISTS technova_reservas;
USE technova_reservas;

-- Tabla de usuarios que pueden hacer reservas
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de salas disponibles para reservar
CREATE TABLE IF NOT EXISTS salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    capacidad INT NOT NULL,
    ubicacion VARCHAR(200) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de reservas: relaciona usuarios con salas en un horario
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    sala_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',  -- activa | cancelada
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- Datos de ejemplo para probar el sistema
INSERT INTO usuarios (nombre, email) VALUES
    ('Zeus Ramirez', 'zeus@technova.com'),
    ('Ana Lopez', 'ana@technova.com');

INSERT INTO salas (nombre, capacidad, ubicacion) VALUES
    ('Sala Alfa', 10, 'Piso 1 - Ala Norte'),
    ('Sala Beta', 5, 'Piso 2 - Ala Sur'),
    ('Sala Gamma', 20, 'Piso 3 - Centro');
