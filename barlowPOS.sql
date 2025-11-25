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
    dni VARCHAR(20),
    nombre VARCHAR(100) NOT NULL
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
    id_pedido INT PRIMARY KEY,
    total DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_usuario INT NOT NULL,
    id_mesa INT NOT NULL,
    CONSTRAINT pedidos_usuario_fk FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),
    CONSTRAINT pedidos_mesa_fk FOREIGN KEY (id_mesa)
        REFERENCES mesas(id_mesa)
);

CREATE TABLE detalles_de_ventas (
    id_detalle INT PRIMARY KEY,
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
    id_usuario INT NOT NULL,
    CONSTRAINT check_tipo_pago CHECK (tipo_pago IN ('efectivo', 'tarjeta', 'transferencia', 'qr')),
    CONSTRAINT pagos_pedido_fk FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    CONSTRAINT pagos_usuario_fk FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);

CREATE TABLE comprobantes (
    id_comprobante INT PRIMARY KEY,
    tipo_comprobante VARCHAR(10) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_cliente INT NOT NULL,
    id_pago INT NOT NULL UNIQUE,
    CONSTRAINT check_tipo_comp CHECK (tipo_comprobante IN ('boleta', 'factura')),
    CONSTRAINT comp_cliente_fk FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente),
    CONSTRAINT comp_pago_fk FOREIGN KEY (id_pago)
        REFERENCES pagos(id_pago) ON DELETE CASCADE
);

CREATE TABLE boletas (
    id_boleta INT PRIMARY KEY,
    nombre VARCHAR(100),
    serie_especifica VARCHAR(50) NOT NULL,
    datos_electronicos VARCHAR(4000),
    id_comprobante INT NOT NULL UNIQUE,
    CONSTRAINT boletas_comp_fk FOREIGN KEY (id_comprobante)
        REFERENCES comprobantes(id_comprobante) ON DELETE CASCADE
);

CREATE TABLE facturas (
    id_factura INT PRIMARY KEY,
    ruc VARCHAR(20) NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    id_comprobante INT NOT NULL UNIQUE,
    CONSTRAINT facturas_comp_fk FOREIGN KEY (id_comprobante)
        REFERENCES comprobantes(id_comprobante) ON DELETE CASCADE
);


INSERT INTO roles (id_rol, nombre, permisos) VALUES (1, 'Administrador', 'todos');
INSERT INTO roles (id_rol, nombre, permisos) VALUES (2, 'Cajero', 'pagos, pedidos');

INSERT INTO clasificaciones (id_clasificacion, nombre) VALUES (1, 'Bebida');
INSERT INTO clasificaciones (id_clasificacion, nombre) VALUES (2, 'Plato principal');

INSERT INTO ambientes (id_ambiente, nombre) VALUES (1, 'Salón principal');
INSERT INTO ambientes (id_ambiente, nombre) VALUES (2, 'Terraza');

INSERT INTO mesas (id_mesa, numero, estado, id_ambiente) VALUES (1, 10, 'disponible', 1);
INSERT INTO mesas (id_mesa, numero, estado, id_ambiente) VALUES (2, 5, 'ocupada', 2);

INSERT INTO clientes (id_cliente, dni, nombre) VALUES (1, '71234567', 'María Gómez');
INSERT INTO clientes (id_cliente, dni, nombre) VALUES (2, '82345678', 'Luis Fernández');

INSERT INTO usuarios (id_usuario, nombre, credenciales, acceso, id_rol)
VALUES (1, 'Ana Admin', 'hash123', 'activo', 1);
INSERT INTO usuarios (id_usuario, nombre, credenciales, acceso, id_rol)
VALUES (2, 'Carlos Cajero', 'hash456', 'activo', 2);

INSERT INTO productos (id_producto, nombre, precio_base, tipo_producto, tiempo_preparacion, es_vegetariano, volumen_ml, contenido_alcohol, id_clasificaciones)
VALUES (1, 'Cerveza IPA', 12.50, 'Bebida', NULL, 'N', 500, 5.5, 1);
INSERT INTO productos (id_producto, nombre, precio_base, tipo_producto, tiempo_preparacion, es_vegetariano, volumen_ml, contenido_alcohol, id_clasificaciones)
VALUES (2, 'Lomo Saltado', 28.00, 'Plato', 15, 'N', NULL, NULL, 2);

INSERT INTO pedidos (id_pedido, total, fecha, id_usuario, id_mesa)
VALUES (1, 40.50, NOW(), 2, 2);

INSERT INTO detalles_de_ventas (id_detalle, id_pedido, id_producto, cantidad, precio_unitario)
VALUES (1, 1, 1, 1, 12.50);
INSERT INTO detalles_de_ventas (id_detalle, id_pedido, id_producto, cantidad, precio_unitario)
VALUES (2, 1, 2, 1, 28.00);

INSERT INTO pagos (id_pago, monto_entregado, vuelto, tipo_pago, id_pedido, id_usuario)
VALUES (1, 50.00, 9.50, 'efectivo', 1, 2);

INSERT INTO comprobantes (id_comprobante, tipo_comprobante, fecha, id_cliente, id_pago)
VALUES (1, 'boleta', NOW(), 1, 1);

INSERT INTO boletas (id_boleta, nombre, serie_especifica, datos_electronicos, id_comprobante)
VALUES (1, 'Boleta de Venta', 'B001-0001', 'QR: ...', 1);