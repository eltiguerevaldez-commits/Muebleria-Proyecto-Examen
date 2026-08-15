-- =====================================================================
-- SISTEMA DE GESTION DE VENTAS - CARIBBEAN FURNITURE STORE SRL
-- Examen Final - Programacion II
-- Motor: MySQL 8.x
-- Convertido desde PostgreSQL + ampliado con creditos, cuentas por
-- cobrar y triggers segun los requisitos del examen.
-- =====================================================================

DROP DATABASE IF EXISTS caribbean_furniture;
CREATE DATABASE caribbean_furniture CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE caribbean_furniture;

-- =====================================================================
-- TABLA: usuarios  (usuarios del sistema / acceso al sistema)
-- =====================================================================
CREATE TABLE usuarios (
    id_usuario   INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    usuario      VARCHAR(50)  NOT NULL UNIQUE,
    clave        VARCHAR(255) NOT NULL,
    rol          VARCHAR(20)  NOT NULL DEFAULT 'Vendedor'
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: categorias
-- =====================================================================
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    descripcion  TEXT
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: clientes
-- =====================================================================
CREATE TABLE clientes (
    id_cliente     INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    apellido       VARCHAR(100),
    cedula         VARCHAR(20)  NOT NULL UNIQUE,
    telefono       VARCHAR(20),
    direccion      TEXT,
    correo         VARCHAR(100),
    limite_credito DECIMAL(10,2) NOT NULL DEFAULT 0,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: proveedores
-- =====================================================================
CREATE TABLE proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    empresa      VARCHAR(100),
    telefono     VARCHAR(20),
    correo       VARCHAR(100),
    direccion    TEXT,
    estado       VARCHAR(20) NOT NULL DEFAULT 'Activo'
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: productos
-- =====================================================================
CREATE TABLE productos (
    id_producto  INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nombre       VARCHAR(100) NOT NULL,
    descripcion  TEXT,
    material     VARCHAR(50),
    color        VARCHAR(50),
    precio       DECIMAL(10,2) NOT NULL,
    stock        INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: compras (a proveedores, para reponer inventario)
-- =====================================================================
CREATE TABLE compras (
    id_compra     INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor  INT NOT NULL,
    id_usuario    INT NOT NULL,
    fecha         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal      DECIMAL(10,2) NOT NULL,
    itbis         DECIMAL(10,2) NOT NULL,
    total         DECIMAL(10,2) NOT NULL,
    observaciones TEXT,
    CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    CONSTRAINT fk_compra_usuario   FOREIGN KEY (id_usuario)   REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: detalle_compras
-- =====================================================================
CREATE TABLE detalle_compras (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_compra         INT NOT NULL,
    id_producto       INT NOT NULL,
    cantidad          INT NOT NULL,
    costo_unitario    DECIMAL(10,2) NOT NULL,
    subtotal          DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_detalle_compra          FOREIGN KEY (id_compra)   REFERENCES compras(id_compra) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto_compra FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: facturas  (cabecera de venta -> contado o credito)
-- =====================================================================
CREATE TABLE facturas (
    id_factura     INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente     INT NOT NULL,
    id_usuario     INT NOT NULL,
    fecha          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_venta     ENUM('Contado','Credito') NOT NULL,
    plazo_dias     INT NULL COMMENT '30, 45 o 60 dias. NULL si es contado',
    subtotal       DECIMAL(10,2) NOT NULL,
    itbis          DECIMAL(10,2) NOT NULL,
    total          DECIMAL(10,2) NOT NULL,
    metodo_pago    VARCHAR(30) NOT NULL DEFAULT 'Efectivo',
    estado         ENUM('Activa','Anulada') NOT NULL DEFAULT 'Activa',
    CONSTRAINT fk_factura_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT fk_factura_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    CONSTRAINT chk_plazo CHECK (
        (tipo_venta = 'Contado' AND plazo_dias IS NULL) OR
        (tipo_venta = 'Credito' AND plazo_dias IN (30,45,60))
    )
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: detalle_factura (lineas de cada factura)
-- =====================================================================
CREATE TABLE detalle_factura (
    id_detalle   INT AUTO_INCREMENT PRIMARY KEY,
    id_factura   INT NOT NULL,
    id_producto  INT NOT NULL,
    cantidad     INT NOT NULL,
    precio       DECIMAL(10,2) NOT NULL,
    subtotal     DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_detalle_factura  FOREIGN KEY (id_factura)  REFERENCES facturas(id_factura) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: cuentas_por_cobrar (se llena automaticamente via trigger
--         cuando una factura es a credito)
-- =====================================================================
CREATE TABLE cuentas_por_cobrar (
    id_cxc            INT AUTO_INCREMENT PRIMARY KEY,
    id_factura        INT NOT NULL,
    id_cliente        INT NOT NULL,
    fecha_emision     DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    monto_total       DECIMAL(10,2) NOT NULL,
    saldo_pendiente   DECIMAL(10,2) NOT NULL,
    estado            ENUM('Pendiente','Pagada','Vencida') NOT NULL DEFAULT 'Pendiente',
    CONSTRAINT fk_cxc_factura FOREIGN KEY (id_factura) REFERENCES facturas(id_factura),
    CONSTRAINT fk_cxc_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
) ENGINE=InnoDB;

-- =====================================================================
-- TABLA: pagos (abonos a las cuentas por cobrar)
-- =====================================================================
CREATE TABLE pagos (
    id_pago      INT AUTO_INCREMENT PRIMARY KEY,
    id_cxc       INT NOT NULL,
    fecha_pago   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto        DECIMAL(10,2) NOT NULL,
    metodo_pago  VARCHAR(30) NOT NULL DEFAULT 'Efectivo',
    CONSTRAINT fk_pago_cxc FOREIGN KEY (id_cxc) REFERENCES cuentas_por_cobrar(id_cxc)
) ENGINE=InnoDB;

-- =====================================================================
-- TRIGGERS
-- =====================================================================

DELIMITER $$

-- 1) Al insertar una factura de CREDITO, generar automaticamente
--    su registro en cuentas_por_cobrar con la fecha de vencimiento
--    calculada segun el plazo (30/45/60 dias)
CREATE TRIGGER trg_factura_credito
AFTER INSERT ON facturas
FOR EACH ROW
BEGIN
    IF NEW.tipo_venta = 'Credito' THEN
        INSERT INTO cuentas_por_cobrar (id_factura, id_cliente, fecha_emision, fecha_vencimiento, monto_total, saldo_pendiente, estado)
        VALUES (
            NEW.id_factura,
            NEW.id_cliente,
            DATE(NEW.fecha),
            DATE_ADD(DATE(NEW.fecha), INTERVAL NEW.plazo_dias DAY),
            NEW.total,
            NEW.total,
            'Pendiente'
        );
    END IF;
END$$

-- 2) Al insertar una linea de detalle de factura, descontar el
--    stock del producto vendido automaticamente
CREATE TRIGGER trg_descontar_stock
AFTER INSERT ON detalle_factura
FOR EACH ROW
BEGIN
    UPDATE productos
       SET stock = stock - NEW.cantidad
     WHERE id_producto = NEW.id_producto;
END$$

-- 3) Evitar vender mas cantidad de la que hay en existencia
CREATE TRIGGER trg_validar_stock
BEFORE INSERT ON detalle_factura
FOR EACH ROW
BEGIN
    DECLARE stock_actual INT;
    SELECT stock INTO stock_actual FROM productos WHERE id_producto = NEW.id_producto;
    IF stock_actual < NEW.cantidad THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Stock insuficiente para completar la venta de este producto';
    END IF;
END$$

-- 4) Al registrar un pago, actualizar el saldo pendiente de la
--    cuenta por cobrar y marcarla como Pagada si el saldo llega a 0
CREATE TRIGGER trg_actualizar_saldo
AFTER INSERT ON pagos
FOR EACH ROW
BEGIN
    UPDATE cuentas_por_cobrar
       SET saldo_pendiente = saldo_pendiente - NEW.monto,
           estado = CASE WHEN (saldo_pendiente - NEW.monto) <= 0 THEN 'Pagada' ELSE estado END
     WHERE id_cxc = NEW.id_cxc;
END$$

-- 5) Al insertar el detalle de una COMPRA a un proveedor, aumentar
--    el stock del producto comprado automaticamente
CREATE TRIGGER trg_aumentar_stock_compra
AFTER INSERT ON detalle_compras
FOR EACH ROW
BEGIN
    UPDATE productos
       SET stock = stock + NEW.cantidad
     WHERE id_producto = NEW.id_producto;
END$$

DELIMITER ;

-- =====================================================================
-- DATOS REALES DE CARIBBEAN FURNITURE STORE SRL
-- =====================================================================

-- Usuarios (se agrega un admin adicional con clave mas segura; se
-- conserva el usuario original del negocio: admin / 1234)
INSERT INTO usuarios (nombre, usuario, clave, rol) VALUES
('Administrador', 'admin', '1234', 'Administrador');

-- Categorias
INSERT INTO categorias (nombre, descripcion) VALUES
('Sala', 'Muebles para la sala'),
('Comedor', 'Muebles para el comedor'),
('Dormitorio', 'Muebles para habitaciones'),
('Oficina', 'Muebles de oficina'),
('Cocina', 'Muebles para cocina'),
('Exterior', 'Muebles para terrazas y jardines');

-- Clientes (limite_credito no existia en el dump original; se deja en 0
-- por defecto, ajustalo desde la app si algun cliente debe tener credito)
INSERT INTO clientes (nombre, apellido, cedula, telefono, direccion, correo, limite_credito, fecha_registro) VALUES
('Carlos', 'Rodriguez', '40200000000', '8090000000', 'Santo Domingo', 'carlos@email.com', 0, '2026-08-07 03:16:13'),
('Juan', 'Matos', '123456789', '8095551234', 'Santo Domingo', 'juan@email.com', 0, '2026-08-07 03:36:14'),
('Juan', 'Pérez', '40200000003', '8090000003', 'Santo Domingo', 'juan.perez@email.com', 0, '2026-08-07 03:41:57'),
('Ana', 'Martínez', '40200000004', '8090000004', 'Santiago', 'ana.martinez@email.com', 0, '2026-08-07 03:41:57'),
('Luis', 'Fernández', '40200000005', '8090000005', 'San Pedro de Macorís', 'luis.fernandez@email.com', 0, '2026-08-07 03:41:57'),
('Carmen', 'Díaz', '40200000006', '8090000006', 'La Vega', 'carmen.diaz@email.com', 0, '2026-08-07 03:41:57'),
('Pedro', 'Ramírez', '40200000007', '8090000007', 'Puerto Plata', 'pedro.ramirez@email.com', 0, '2026-08-07 03:41:57'),
('Laura', 'Santos', '40200000008', '8090000008', 'San Cristóbal', 'laura.santos@email.com', 0, '2026-08-07 03:41:57'),
('Miguel', 'Castillo', '40200000009', '8090000009', 'Puerto Plata', 'miguel.castillo@email.com', 0, '2026-08-07 03:41:57'),
('Sofía', 'Morales', '40200000010', '8090000010', 'Bonao', 'sofia.morales@email.com', 0, '2026-08-07 03:41:57'),
('José', 'Núñez', '40200000011', '8090000011', 'Moca', 'jose.nunez@email.com', 0, '2026-08-07 03:41:57'),
('Daniela', 'Herrera', '40200000012', '8090000012', 'San Juan', 'daniela.herrera@email.com', 0, '2026-08-07 03:41:57'),
('Andrés', 'Torres', '40200000013', '8090000013', 'Higüey', 'andres.torres@email.com', 0, '2026-08-07 03:41:57'),
('Patricia', 'Vargas', '40200000014', '8090000014', 'La Romana', 'patricia.vargas@email.com', 0, '2026-08-07 03:41:57'),
('Roberto', 'Cruz', '40200000015', '8090000015', 'San Francisco de Macorís', 'roberto.cruz@email.com', 0, '2026-08-07 03:41:57'),
('Natalia', 'Reyes', '40200000016', '8090000016', 'San Francisco de Macorís', 'natalia.reyes@email.com', 0, '2026-08-07 03:41:57'),
('Fernando', 'Mejía', '40200000017', '8090000017', 'Santiago', 'fernando.mejia@email.com', 0, '2026-08-07 03:41:57'),
('Gabriela', 'Peña', '40200000018', '8090000018', 'Santo Domingo', 'gabriela.pena@email.com', 0, '2026-08-07 03:41:57');

-- Productos
INSERT INTO productos (id_categoria, nombre, descripcion, material, color, precio, stock) VALUES
(1, 'Sofá 3 Plazas', 'Sofá moderno de tres plazas', 'Madera', 'Gris', 35000.00, 5),
(1, 'Sofá Esquinero', 'Sofá en forma de L', 'Caoba', 'Beige', 48000.00, 3),
(1, 'Mesa de Centro', 'Mesa de centro de cristal', 'Madera y vidrio', 'Negro', 9500.00, 10),
(1, 'Mueble para TV', 'Centro de entretenimiento', 'Melamina', 'Blanco', 18500.00, 6),
(2, 'Mesa de Comedor', 'Mesa para seis personas', 'Caoba', 'Marrón', 28000.00, 4),
(2, 'Sillas de Comedor', 'Juego de 6 sillas', 'Roble', 'Marrón', 18000.00, 8),
(2, 'Vitrina', 'Vitrina para comedor', 'Caoba', 'Chocolate', 22000.00, 2),
(3, 'Cama Queen', 'Cama tamaño Queen', 'Roble', 'Blanco', 42000.00, 3),
(3, 'Cama King', 'Cama tamaño King', 'Caoba', 'Marrón', 52000.00, 2),
(3, 'Mesa de Noche', 'Mesa de noche con dos gavetas', 'Madera', 'Blanco', 6500.00, 12),
(3, 'Cómoda', 'Cómoda de seis gavetas', 'Roble', 'Gris', 17000.00, 5),
(3, 'Armario', 'Armario de cuatro puertas', 'Caoba', 'Marrón', 39000.00, 4),
(4, 'Escritorio Ejecutivo', 'Escritorio para oficina', 'Melamina', 'Negro', 18000.00, 8),
(4, 'Silla Ejecutiva', 'Silla ergonómica', 'Cuero', 'Negro', 12000.00, 10),
(4, 'Archivador', 'Archivador metálico de 4 gavetas', 'Metal', 'Gris', 9500.00, 6),
(5, 'Gabinete de Cocina', 'Gabinete superior', 'Melamina', 'Blanco', 25000.00, 4),
(5, 'Desayunador', 'Mesa para cocina con 4 sillas', 'Madera', 'Natural', 19500.00, 3),
(6, 'Juego de Terraza', 'Mesa con cuatro sillas para exterior', 'Ratán', 'Marrón', 31000.00, 2),
(6, 'Silla de Jardín', 'Silla plástica reforzada', 'Plástico', 'Blanco', 2800.00, 20),
(6, 'Banco de Jardín', 'Banco para exterior', 'Hierro y madera', 'Negro', 9800.00, 5);

-- Proveedores
INSERT INTO proveedores (nombre, empresa, telefono, correo, direccion, estado) VALUES
('Carlos Rodríguez', 'Muebles RD', '809-555-1001', 'ventas@mueblesrd.com', 'Santo Domingo', 'Activo'),
('Ana Pérez', 'Caoba Dominicana', '809-555-1002', 'contacto@caobard.com', 'Santiago', 'Activo'),
('Luis Gómez', 'Muebles Modernos', '809-555-1003', 'info@mueblesmodernos.com', 'La Romana', 'Activo'),
('María López', 'Decor Hogar', '809-555-1004', 'ventas@decorhogar.com', 'San Pedro de Macorís', 'Activo'),
('José Martínez', 'Muebles del Este', '809-555-1005', 'jmartinez@muebleseste.com', 'La Altagracia', 'Activo'),
('Laura Sánchez', 'Elegance Furniture', '809-555-1006', 'laura@elegance.com', 'Santo Domingo', 'Activo'),
('Pedro Castillo', 'Diseños en Madera', '809-555-1007', 'ventas@disenosmadera.com', 'San Cristóbal', 'Activo'),
('Carmen Díaz', 'Hogar Ideal', '809-555-1008', 'carmen@hogarideal.com', 'La Vega', 'Activo'),
('Miguel Fernández', 'Muebles Premium', '809-555-1009', 'miguel@premium.com', 'Puerto Plata', 'Activo'),
('Patricia Herrera', 'Casa Moderna', '809-555-1010', 'patricia@casamoderna.com', 'Santiago', 'Activo'),
('Andrés Ramírez', 'Mobiliario Nacional', '809-555-1011', 'andres@mobiliario.com', 'Santo Domingo', 'Activo'),
('Daniela Cruz', 'Confort Home', '809-555-1012', 'daniela@conforthome.com', 'Higüey', 'Activo'),
('Víctor Núñez', 'Roble Furniture', '809-555-1013', 'ventas@roblefurniture.com', 'San Francisco de Macorís', 'Activo'),
('Natalia Mejía', 'Decoraciones Mejía', '809-555-1014', 'natalia@decoraciones.com', 'Moca', 'Activo'),
('Fernando Ortiz', 'Muebles Ortiz', '809-555-1015', 'fernando@ortiz.com', 'Baní', 'Activo'),
('Rosa Jiménez', 'Innova Hogar', '809-555-1016', 'rosa@innovahogar.com', 'Azua', 'Activo'),
('Ricardo Santos', 'Factory Muebles', '809-555-1017', 'ricardo@factorymuebles.com', 'Santo Domingo', 'Activo'),
('Paola García', 'Muebles García', '809-555-1018', 'paola@mueblesgarcia.com', 'San Juan', 'Activo'),
('Héctor Morales', 'Arte en Madera', '809-555-1019', 'hector@artemadera.com', 'Barahona', 'Activo'),
('Gabriela Torres', 'Luxury Home', '809-555-1020', 'gabriela@luxuryhome.com', 'Samaná', 'Activo');

-- NOTA: la compra original del dump se omite aqui porque insertaria doble
-- el stock (el trigger trg_aumentar_stock_compra ya suma el stock al
-- registrar el detalle_compra, y el stock de "productos" arriba ya viene
-- con el stock final real). Si quieres tambien el historial de esa compra
-- inicial, descomenta las siguientes lineas (y resta esas cantidades del
-- stock de productos de arriba para que no quede duplicado):
--
-- INSERT INTO compras (id_proveedor, id_usuario, fecha, subtotal, itbis, total, observaciones) VALUES
-- (1, 1, '2026-08-05 17:22:56', 50000.00, 9000.00, 59000.00, 'Compra inicial de mercancía');
-- INSERT INTO detalle_compras (id_compra, id_producto, cantidad, costo_unitario, subtotal) VALUES
-- (1, 1, 5, 25000.00, 125000.00),
-- (1, 2, 3, 35000.00, 105000.00),
-- (1, 8, 2, 30000.00, 60000.00);
