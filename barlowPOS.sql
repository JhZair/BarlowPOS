DROP DATABASE IF EXISTS barlow_db;
CREATE DATABASE barlow_db;
USE barlow_db;

CREATE TABLE roles (
    id_rol INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    permisos VARCHAR(4000) NOT NULL
);

CREATE TABLE clasificaciones (
    id_clasificacion INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE ambientes (
    id_ambiente INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE mesas (
    id_mesa INT PRIMARY KEY,
    numero INT NOT NULL,
    estado VARCHAR(20) DEFAULT 'disponible' NOT NULL,
    id_ambiente INT NOT NULL,
    CONSTRAINT check_estado_mesa CHECK (estado IN ('disponible', 'ocupada', 'reservada')),
    CONSTRAINT mesas_ambiente_fk FOREIGN KEY (id_ambiente)
        REFERENCES ambientes(id_ambiente)
);

CREATE TABLE clientes (
    id_cliente INT PRIMARY KEY,
    direccion VARCHAR(150),
    telefono VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE personas_naturales (
    id_cliente INT PRIMARY KEY,
    dni VARCHAR(8) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    CONSTRAINT pn_cliente_fk FOREIGN KEY (id_cliente) 
        REFERENCES clientes(id_cliente) ON DELETE CASCADE
);

CREATE TABLE personas_juridicas (
    id_cliente INT PRIMARY KEY,
    ruc VARCHAR(11) NOT NULL UNIQUE,
    razon_social VARCHAR(150) NOT NULL,
    CONSTRAINT pj_cliente_fk FOREIGN KEY (id_cliente) 
        REFERENCES clientes(id_cliente) ON DELETE CASCADE
);

CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    credenciales VARCHAR(255) NOT NULL,
    acceso VARCHAR(10) DEFAULT 'activo' NOT NULL,
    id_rol INT NOT NULL,
    CONSTRAINT check_acceso_usuario CHECK (acceso IN ('activo', 'inactivo')),
    CONSTRAINT usuarios_rol_fk FOREIGN KEY (id_rol)
        REFERENCES roles(id_rol)
);

CREATE TABLE productos (
    id_producto INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    tipo_producto VARCHAR(50),
    tiempo_preparacion INT, -- minutos
    es_vegetariano CHAR(1),
    volumen_ml INT,
    contenido_alcohol DECIMAL(5,2),
    id_clasificaciones INT NOT NULL,
    CONSTRAINT check_vegetariano CHECK (es_vegetariano IN ('Y', 'N')),
    CONSTRAINT productos_clasif_fk FOREIGN KEY (id_clasificaciones)
        REFERENCES clasificaciones(id_clasificacion)
);

CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    total DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_usuario INT NOT NULL,
    id_mesa INT NOT NULL,
    CONSTRAINT pedidos_usuario_fk FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),
    CONSTRAINT pedidos_mesa_fk FOREIGN KEY (id_mesa)
        REFERENCES mesas(id_mesa)
);

CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_mesa INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_mesa) REFERENCES mesas(id_mesa)
);

CREATE TABLE detalles_de_ventas (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT check_cantidad CHECK (cantidad > 0),
    CONSTRAINT dv_pedido_fk FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    CONSTRAINT dv_producto_fk FOREIGN KEY (id_producto)
        REFERENCES productos(id_producto)
);

CREATE TABLE pagos (
    id_pago INT PRIMARY KEY,
    monto_entregado DECIMAL(10,2) NOT NULL,
    vuelto DECIMAL(10,2),
    tipo_pago VARCHAR(20) NOT NULL,
    ultimos_4_digitos VARCHAR(4),
    tecnologia VARCHAR(50),
    num_autorizacion VARCHAR(50),
    plataforma VARCHAR(50),
    id_pedido INT NOT NULL,
    id_usuario INT NOT NULL, -- Quién cobró
    CONSTRAINT check_tipo_pago CHECK (tipo_pago IN ('efectivo', 'tarjeta', 'transferencia', 'qr')),
    CONSTRAINT pagos_pedido_fk FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    CONSTRAINT pagos_usuario_fk FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);

CREATE TABLE comprobantes (
    id_comprobante INT PRIMARY KEY,
    id_pedido INT NOT NULL UNIQUE, 
    id_cliente INT NOT NULL,
    fecha_emision DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    total_gravada DECIMAL(10,2) NOT NULL, -- Base imponible (sin IGV)
    total_igv DECIMAL(10,2) NOT NULL,     -- El 18%
    total_importe DECIMAL(10,2) NOT NULL, -- El total final
    CONSTRAINT comp_pedido_fk FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    CONSTRAINT comp_cliente_fk FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE boletas (
    id_comprobante INT PRIMARY KEY,
    serie VARCHAR(4) NOT NULL,
    correlativo INT NOT NULL,
    datos_electronicos VARCHAR(4000),  
    CONSTRAINT boletas_comp_fk FOREIGN KEY (id_comprobante)
        REFERENCES comprobantes(id_comprobante) ON DELETE CASCADE
);

CREATE TABLE facturas (
    id_comprobante INT PRIMARY KEY,
    serie VARCHAR(4) NOT NULL,
    correlativo INT NOT NULL,
    datos_electronicos VARCHAR(4000),
    CONSTRAINT facturas_comp_fk FOREIGN KEY (id_comprobante)
        REFERENCES comprobantes(id_comprobante) ON DELETE CASCADE
);


INSERT INTO roles (id_rol, nombre, permisos) VALUES (1, 'Administrador', 'todos');
INSERT INTO roles (id_rol, nombre, permisos) VALUES (2, 'Cajero', 'pagos, pedidos');
INSERT INTO roles (id_rol, nombre, permisos) VALUES 
(3, 'Mozo', 'pedidos'),
(4, 'Chef', 'cocina'),
(5, 'Almacenero', 'insumos');

INSERT INTO clasificaciones (id_clasificacion, nombre) VALUES (1, 'Bebida');
INSERT INTO clasificaciones (id_clasificacion, nombre) VALUES (2, 'Plato principal');
INSERT INTO clasificaciones (id_clasificacion, nombre) VALUES 
(3, 'Guarnición'),
(4, 'Postre'),
(5, 'Cóctel');
INSERT INTO clasificaciones VALUES (6, 'Entrada');

INSERT INTO ambientes (id_ambiente, nombre) VALUES (1, 'Salón principal');
INSERT INTO ambientes (id_ambiente, nombre) VALUES (2, 'Terraza');
INSERT INTO ambientes (id_ambiente, nombre) VALUES 
(3, 'Barra'),
(4, 'Segundo Piso'),
(5, 'Zona VIP');

INSERT INTO mesas (id_mesa, numero, estado, id_ambiente) VALUES (1, 10, 'disponible', 1);
INSERT INTO mesas (id_mesa, numero, estado, id_ambiente) VALUES (2, 5, 'ocupada', 2);
INSERT INTO mesas (id_mesa, numero, estado, id_ambiente) VALUES 
(3, 11, 'disponible', 1),
(4, 20, 'reservada', 2),
(5, 50, 'disponible', 3);
INSERT INTO mesas VALUES (6, 14, 'disponible', 1)   ;
INSERT INTO mesas VALUES (7, 12, 'reservada', 1);
INSERT INTO mesas VALUES (8, 6, 'disponible', 2);

INSERT INTO clientes (id_cliente, direccion, telefono, email) VALUES 
(1, 'Av. Siempre Viva 123', '900100200', 'juan@mail.com'),
(2, 'Calle Los Pinos 456', '900300400', 'ana@mail.com'),
(3, 'Jr. La Unión 789', '900500600', 'pedro@mail.com');

INSERT INTO personas_naturales (id_cliente, dni, nombres, apellidos) VALUES 
(1, '09876543', 'Juan', 'Pérez'),
(2, '11223344', 'Ana', 'Lima'),
(3, '55667788', 'Pedro', 'Castillo');

INSERT INTO personas_juridicas (id_cliente, ruc, razon_social) VALUES 
(3, '20100100101', 'Soluciones Tecnológicas SAC');

INSERT INTO usuarios (id_usuario, nombre, credenciales, acceso, id_rol)
VALUES (1, 'Ana Admin', 'hash123', 'activo', 1);
INSERT INTO usuarios (id_usuario, nombre, credenciales, acceso, id_rol)
VALUES (2, 'Carlos Cajero', 'hash456', 'activo', 2);
INSERT INTO usuarios (id_usuario, nombre, credenciales, acceso, id_rol) VALUES 
(3, 'Marcos Mozo', 'hash789', 'activo', 3),
(4, 'Chefcito Ratatouille', 'hash321', 'activo', 4),
(5, 'Alma Cenero', 'hash654', 'inactivo', 5);

INSERT INTO productos (id_producto, nombre, precio_base, tipo_producto, tiempo_preparacion, es_vegetariano, volumen_ml, contenido_alcohol, id_clasificaciones)
VALUES (1, 'Cerveza IPA', 12.50, 'Bebida', NULL, 'N', 500, 5.5, 1);
INSERT INTO productos (id_producto, nombre, precio_base, tipo_producto, tiempo_preparacion, es_vegetariano, volumen_ml, contenido_alcohol, id_clasificaciones)
VALUES (2, 'Lomo Saltado', 28.00, 'Plato', 15, 'N', NULL, NULL, 2);
INSERT INTO productos (id_producto, nombre, precio_base, tipo_producto, id_clasificaciones) VALUES 
(3, 'Papas Fritas', 15.00, 'Guarnición', 3),
(4, 'Torta de Chocolate', 18.00, 'Postre', 4),
(5, 'Mojito', 25.00, 'Bebida', 5);
INSERT INTO productos VALUES (6, 'Causa Rellena', 15.00, 'Entrada', 10, 'N', NULL, NULL, 3);
INSERT INTO productos VALUES (7, 'Pisco Sour', 22.00, 'Bebida', 5, 'Y', 250, 40.0, 5);
INSERT INTO productos VALUES (8, 'Suspiro a la Limeña', 12.00, 'Postre', NULL, 'Y', NULL, NULL, 4);

INSERT INTO pedidos (id_pedido, total, fecha, id_usuario, id_mesa)
VALUES (1, 40.50, NOW(), 2, 2);
INSERT INTO pedidos (id_pedido, total, fecha, id_usuario, id_mesa)
VALUES (2, 10.00, NOW(), 5, 1);
INSERT INTO pedidos (id_pedido, total, fecha, id_usuario, id_mesa)
VALUES (3, 210.00, NOW(), 1, 5);

INSERT INTO detalles_de_ventas (id_detalle, id_pedido, id_producto, cantidad, precio_unitario)
VALUES (1, 1, 1, 1, 12.50);
INSERT INTO detalles_de_ventas VALUES (2, 1, 2, 1, 30.00);

INSERT INTO pagos (id_pago, monto_entregado, vuelto, tipo_pago, id_pedido, id_usuario)
VALUES (1, 20.00, 0.00, 'efectivo', 1, 2);
INSERT INTO pagos VALUES (2, 100.00, 0, 'tarjeta', '1234', 'Visa', '001', 'Niubiz', 2, 2);

INSERT INTO comprobantes (id_comprobante, fecha_emision, total_gravada, total_igv, total_importe, id_cliente, id_pedido)
VALUES (1, NOW(), 33.90, 6.10, 40.00, 1, 1),
(2, NOW(), 84.75, 15.25, 100.00, 2, 2);

INSERT INTO boletas (id_boleta, serie, correlativo, datos_electronicos, id_comprobante)
VALUES (1, 'B001', 12345, 'HASH_QR_DATA');

INSERT INTO facturas VALUES (1, 'F001', 567, 'HASH_QR_DATA');

ALTER TABLE detalles_de_ventas MODIFY id_detalle INT AUTO_INCREMENT;

-- Para poder modificar sin que mysql evite el cambio
SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE pedidos MODIFY id_pedido INT AUTO_INCREMENT;

SET FOREIGN_KEY_CHECKS = 1;

USE barlow_db;


/*
-- 1. Crear la cabecera del pedido (Tabla PEDIDOS)
INSERT INTO pedidos (total, id_usuario, id_mesa) 
VALUES (0, 3, 5); -- Mozo ID 3, Mesa ID 5
SET @id_nuevo_pedido = LAST_INSERT_ID();

-- 2. Insertar los platos (Tabla DETALLES_DE_VENTAS)
-- Digamos que pidieron 2 'Lomo Saltado' (id 2)
INSERT INTO detalles_de_ventas (id_detalle, id_pedido, id_producto, cantidad, precio_unitario) 
VALUES (101, @id_nuevo_pedido, 2, 2, 28.00); 

-- 3. Bloquear la mesa (Tabla MESAS)
UPDATE mesas 
SET estado = 'ocupada' 
WHERE id_mesa = 5;
*/