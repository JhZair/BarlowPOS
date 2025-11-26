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

INSERT INTO clientes (id_cliente, dni, nombre) VALUES (1, '71234567', 'María Gómez');
INSERT INTO clientes (id_cliente, dni, nombre) VALUES (2, '82345678', 'Luis Fernández');
INSERT INTO clientes (id_cliente, dni, nombre) VALUES 
(3, '44445555', 'Pedro Castillo'),
(4, '66667777', 'Keiko Fujimori'),
(5, '88889999', 'Alan Garcia');

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

INSERT INTO pedidos (id_pedido, total, fecha, id_usuario, id_mesa)
VALUES (1, 40.50, NOW(), 2, 2);
INSERT INTO pedidos (id_pedido, total, fecha, id_usuario, id_mesa)
VALUES (2, 10.00, NOW(), 5, 1);
INSERT INTO pedidos (id_pedido, total, fecha, id_usuario, id_mesa)
VALUES (3, 210.00, NOW(), 1, 5);

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
USE barlow_db;


CREATE TABLE proveedores (
    id_proveedor INT PRIMARY KEY,
    ruc VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE insumos (
    id_insumo INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL, -- ej: kg, litros, unidades
    stock DECIMAL(10,2) DEFAULT 0,
    id_proveedor INT NOT NULL,
    CONSTRAINT insumos_prov_fk FOREIGN KEY (id_proveedor) 
        REFERENCES proveedores(id_proveedor)
);

INSERT INTO proveedores VALUES (1, '20100100101', 'Distribuidora Licores SAC', '999888777', 'ventas@licores.com');
INSERT INTO proveedores VALUES (2, '20200200202', 'Verduras del Campo EIRL', '988777666', 'contacto@campo.com');
INSERT INTO proveedores VALUES (3, '20300300303', 'Carnes Premium SA', '977666555', 'pedidos@carnes.com');
INSERT INTO proveedores VALUES (4, '20400400404', 'Suministros de Limpieza', '966555444', 'limpieza@suministros.com');
INSERT INTO proveedores VALUES (5, '20500500505', 'Bebidas Gaseosas Peru', '955444333', 'ventas@gaseosas.com');

INSERT INTO insumos VALUES (1, 'Cerveza Artesanal Barril', 'Litros', 50.0, 1);
INSERT INTO insumos VALUES (2, 'Papa Amarilla', 'Kg', 100.0, 2);
INSERT INTO insumos VALUES (3, 'Lomo Fino', 'Kg', 30.0, 3);
INSERT INTO insumos VALUES (4, 'Limón', 'Kg', 20.0, 2);
INSERT INTO insumos VALUES (5, 'Servilletas', 'Paquete', 200.0, 4);

INSERT INTO mesas VALUES (3, 11, 'disponible', 1)   ;
INSERT INTO mesas VALUES (4, 12, 'reservada', 1);
INSERT INTO mesas VALUES (5, 6, 'disponible', 2);

INSERT INTO clientes VALUES (3, '09876543', 'Juan Pérez');
INSERT INTO clientes VALUES (4, '11223344', 'Ana Lima');
INSERT INTO clientes VALUES (5, '55667788', 'Pedro Castillo');

INSERT INTO clasificaciones VALUES (3, 'Entrada');
INSERT INTO clasificaciones VALUES (4, 'Postre');
INSERT INTO clasificaciones VALUES (5, 'Cóctel');

INSERT INTO productos VALUES (3, 'Causa Rellena', 15.00, 'Entrada', 10, 'N', NULL, NULL, 3);
INSERT INTO productos VALUES (4, 'Pisco Sour', 22.00, 'Bebida', 5, 'Y', 250, 40.0, 5);
INSERT INTO productos VALUES (5, 'Suspiro a la Limeña', 12.00, 'Postre', NULL, 'Y', NULL, NULL, 4);