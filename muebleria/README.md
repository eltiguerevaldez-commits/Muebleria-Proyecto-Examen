# Sistema de Gestión de Ventas — Mueblería
Examen Final — Programación II

CRUD en **Python (Tkinter)** + base de datos **MySQL**.

## Requisitos cumplidos
- Ventas al contado y a crédito (30, 45 o 60 días)
- Consulta y reportes de ventas
- Cuentas por cobrar (con registro de pagos/abonos)
- Tablas: clientes, productos, facturas (+ detalle_factura), usuarios, categorías, cuentas_por_cobrar, pagos
- Claves primarias con `AUTO_INCREMENT` (generadores)
- 4 Triggers:
  1. `trg_factura_credito`: genera automáticamente la cuenta por cobrar al facturar a crédito
  2. `trg_descontar_stock`: descuenta el stock del producto al vender
  3. `trg_validar_stock`: bloquea la venta si no hay existencia suficiente
  4. `trg_actualizar_saldo`: actualiza el saldo pendiente al registrar un pago
- Formularios: menú principal, acceso al sistema (login), captura de clientes, captura de productos, punto de venta, generación de factura

## 1. Instalar MySQL
Instala MySQL Server (o XAMPP/WAMP si están en Windows) y asegúrate de que esté corriendo.

## 2. Crear la base de datos
Abre MySQL Workbench, phpMyAdmin, o la terminal, y ejecuta el script:

```
mysql -u root -p < database/muebleria_mysql.sql
```

Esto crea la base de datos `muebleria` con todas las tablas, triggers y datos de ejemplo.

## 3. Configurar la conexión
Abre `app/db/conexion.py` y coloca tu usuario y contraseña de MySQL:

```python
CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "TU_PASSWORD_AQUI",
    "database": "muebleria"
}
```

## 4. Instalar dependencias de Python
```
pip install mysql-connector-python
pip install psycopg2-binary
```

## 5. Ejecutar la aplicación
```
python main.py
```

**Usuario de prueba:** `admin` / **Contraseña:** `1234`

## Estructura del proyecto
```
muebleria/
├── database/
│   └── caribbean_furniture_mysql.sql      -> Script completo de la base de datos
├── app/
│   ├── db/
│   │   └── conexion.py          -> Conexión a MySQL
│   ├── screens/
│   │   ├── login.py             -> Acceso al sistema
│   │   ├── menu_principal.py    -> Menú principal
│   │   ├── clientes.py          -> CRUD de clientes
│   │   ├── productos.py         -> CRUD de productos
│   │   ├── punto_venta.py       -> Punto de venta / generar factura
│   │   ├── reportes.py          -> Consultas y reportes de ventas
│   │   └── cuentas_por_cobrar.py -> Cuentas por cobrar y pagos
│   └── utilidades.py            -> Colores, fuentes, formato de moneda
└── main.py                      -> Punto de entrada / navegación
```

## Notas para la exposición
- El script SQL ya fue probado: los triggers funcionan correctamente (descuento de stock, generación automática de cuentas por cobrar, validación de stock insuficiente, actualización de saldos).
- Puedes agregar más usuarios, clientes o productos desde la misma aplicación o editando el `INSERT` inicial del script SQL.
