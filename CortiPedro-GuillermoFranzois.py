# Imports necesarios:
# sqlite3: manejo de base de datos
# datetime: fechas
# time: sleep()
# from typing import List, Tuple, Optional: Para anotaciones de tipo que mejoran la legibilidad y verificación de tipos
# Imports necesarios:
import sqlite3
import datetime
import time
import os
from typing import List, Tuple, Optional
# adaptadores para manejo de fechas en SQLite
def adaptar_fecha(fecha: datetime.datetime) -> str:
    """Adapta datetime a string ISO 8601 para SQLite"""
    return fecha.isoformat()

def convertir_fecha(valor: bytes) -> datetime.datetime:
    """Convierte string ISO 8601 a datetime"""
    return datetime.datetime.fromisoformat(valor.decode())

# Registrar los adaptadores para manejo de fechas
sqlite3.register_adapter(datetime.datetime, adaptar_fecha)
sqlite3.register_converter("fecha", convertir_fecha)
# Definicion de conexión y cursor    
conexion = sqlite3.connect("kiosko.db")
cursor = conexion.cursor()

# Script de creación de tablas
sql_script = """CREATE TABLE IF NOT EXISTS productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER NOT NULL,
    estado INTEGER NOT NULL DEFAULT 1 
);

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    contacto TEXT,
    estado INTEGER NOT NULL DEFAULT 1 
);

CREATE TABLE IF NOT EXISTS producto_proveedor (
    id_relacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER,
    id_proveedor INTEGER,
    precio_compra REAL NOT NULL,
    estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE IF NOT EXISTS compras (
    id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER,
    id_proveedor INTEGER,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    precio_total REAL NOT NULL,
    fecha_compra DATETIME NOT NULL,
    estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE IF NOT EXISTS ventas (
    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    precio_total REAL NOT NULL,
    fecha_venta DATETIME NOT NULL,
    estado INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);"""

cursor.executescript(sql_script)
conexion.commit()
conexion.close()

# Función para reconocer cadenas vacias
def es_vacia(str_evaluar):
    if str_evaluar.strip() == "":
        return True
    else:
        return False

# Función de confirmación:
def confirmarFN():
    op_validas = [0,1]
    while True:
        confirmar = input("Desea confirmar su acción? Ingrese 1 para hacerlo o 0 para cancelarlo: ")
        try:
            confirmar_int = int(confirmar)
            if confirmar_int not in op_validas:
                print("Error: Debe ingresar una opción válida (0,1). Intente nuevamente.")
            else:
                return confirmar_int == 1
        except ValueError:
            print("Error: Debe ingresar un número (0 o 1). Intente nuevamente.")

# Función impresora de menus:
def mostrar_menus(tipo_menu = int):
    if tipo_menu == 1:
        print("\n<--- Gestión de Productos ---> \n1. Agregar producto\n2. Modificar producto\n3. Eliminar (desactivar) producto\n4. Listar productos activos\n5. Volver al menú principal")
    elif tipo_menu == 2:
        print("\n<--- Gestión de Proveedores --->\n1. Agregar proveedor\n2. Modificar proveedor\n3. Desactivar proveedor\n4. Listar proveedores activos\n5. Volver al menú principal")
    elif tipo_menu == 3:
        print("\n<--- Gestión de Registros --->\n1. Registrar compra\n2. Registrar venta\n3. Mostrar registros de compras\n4. Mostrar registros de ventas\n5. Exportar registros a archivo\n6. Volver al menú principal")

# Funciones productos
def agregar_producto():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    try:
        nombre = input("Ingrese el nombre del producto: ")
        while es_vacia(nombre):
            print("Error: El nombre no puede estar vacío.")
            nombre = input("Ingrese el nombre del producto: ")
            
        categoria = input("Ingrese la categoria: ")
        while es_vacia(categoria):
            print("Error: La categoría no puede estar vacía.")
            categoria = input("Ingrese la categoria: ")
            
        precio = float(input("Ingrese el precio del producto: "))
        while precio <= 0:
            print("Error: El precio debe ser mayor a 0.")
            precio = float(input("Ingrese el precio del producto: "))
            
        stock = int(input("Ingrese el stock inicial del producto: "))
        while stock < 0:
            print("Error: El stock no puede ser negativo.")
            stock = int(input("Ingrese el stock inicial del producto: "))
            
        cursor.execute("INSERT INTO productos (nombre, categoria, precio, stock, estado) VALUES (?, ?, ?, ?, 1)",
        (nombre, categoria, precio, stock))
        conexion.commit()
        print("Producto agregado correctamente.")
    except ValueError:
        print("Error: Ingrese valores válidos.")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

def modificar_producto():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    try:
        listar_productos()
        id_prod_mod = int(input("Ingrese el id del producto a modificar: "))
        cursor.execute("SELECT * FROM productos WHERE id_producto == ? AND estado == 1", (id_prod_mod,))
        producto = cursor.fetchone()
        
        if producto is None:
            print("No existe un producto activo con ese ID.")
            return
        
        print("\nProducto encontrado:")
        print(f"ID: {producto[0]}")
        print(f"Nombre: {producto[1]}")
        print(f"Categoría: {producto[2]}")
        print(f"Precio: ${producto[3]:.2f}")
        print(f"Stock: {producto[4]}")
        
        nombre_actual = producto[1]
        categoria_actual = producto[2]
        precio_actual = producto[3]
        stock_actual = producto[4]
        
        print("\n¿Qué atributos desea modificar?")
        print("1. Nombre")
        print("2. Categoría")
        print("3. Precio")
        print("4. Stock")
        print("0. Cancelar")
        
        opciones = input("Ingrese los números de las opciones separados por comas (ej: 1,3): ")
        opciones = [op.strip() for op in opciones.split(',') if op.strip().isdigit()]
        
        if not opciones or '0' in opciones:
            print("Modificación cancelada.")
            return
            
        for op in opciones:
            if op == '1':
                nuevo_nombre = input(f"Ingrese nuevo nombre (actual: {nombre_actual}): ")
                if not es_vacia(nuevo_nombre):
                    nombre_actual = nuevo_nombre
            elif op == '2':
                nueva_categoria = input(f"Ingrese nueva categoría (actual: {categoria_actual}): ")
                if not es_vacia(nueva_categoria):
                    categoria_actual = nueva_categoria
            elif op == '3':
                try:
                    nuevo_precio = float(input(f"Ingrese nuevo precio (actual: {precio_actual}): "))
                    if nuevo_precio > 0:
                        precio_actual = nuevo_precio
                    else:
                        print("El precio debe ser mayor a 0. Se mantiene el valor actual.")
                except ValueError:
                    print("Valor inválido. Se mantiene el precio actual.")
            elif op == '4':
                try:
                    nuevo_stock = int(input(f"Ingrese nuevo stock (actual: {stock_actual}): "))
                    if nuevo_stock >= 0:
                        stock_actual = nuevo_stock
                    else:
                        print("El stock no puede ser negativo. Se mantiene el valor actual.")
                except ValueError:
                    print("Valor inválido. Se mantiene el stock actual.")
        
        print("\nResumen de cambios:")
        print(f"Nombre: {nombre_actual}")
        print(f"Categoría: {categoria_actual}")
        print(f"Precio: ${precio_actual:.2f}")
        print(f"Stock: {stock_actual}")
        
        if confirmarFN():
            cursor.execute("UPDATE productos SET nombre=?, categoria=?, precio=?, stock=? WHERE id_producto=?",
                (nombre_actual, categoria_actual, precio_actual, stock_actual, id_prod_mod))
            conexion.commit()
            print("Producto modificado exitosamente.")
        else:
            print("Modificación cancelada.")
            
    except ValueError:
        print("Error: Ingrese un ID válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

def desactivar_productos():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    try:
        listar_productos()
        id_prod_des = int(input("Ingrese el id del producto a desactivar: "))
        cursor.execute("SELECT * FROM productos WHERE id_producto == ? AND estado == 1", (id_prod_des,))
        producto = cursor.fetchone()
        
        if producto is None:
            print("No existe un producto activo con ese ID.")
            return
        
        print("\nProducto encontrado:")
        print(f"ID: {producto[0]}")
        print(f"Nombre: {producto[1]}")
        print(f"Categoría: {producto[2]}")
        print(f"Precio: ${producto[3]:.2f}")
        print(f"Stock: {producto[4]}")
        
        if confirmarFN():
            cursor.execute("UPDATE productos SET estado=? WHERE id_producto=?",
                (0, id_prod_des))
            conexion.commit()
            print("El producto ha sido desactivado exitosamente.")
        else:
            print("Operación cancelada.")
            
    except ValueError:
        print("Error: Ingrese un ID válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

def listar_productos():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT * FROM productos WHERE estado == 1")
        resultados = cursor.fetchall()
        
        if not resultados:
            print("No hay productos activos.")
            return
            
        print("\n=== LISTADO DE PRODUCTOS ===")
        print(f"{'ID':<5} {'Nombre':<20} {'Categoría':<15} {'Precio':<10} {'Stock':<10}")
        print("-" * 60)
        for producto in resultados:
            print(f"{producto[0]:<5} {producto[1]:<20} {producto[2]:<15} ${producto[3]:<9.2f} {producto[4]:<10}")
            
        return resultados
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

# Funciones proveedores
def agregar_proveedor():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    try:
        nombre = input("Ingrese el nombre del proveedor: ")
        while es_vacia(nombre):
            print("Error: El nombre no puede estar vacío.")
            nombre = input("Ingrese el nombre del proveedor: ")
            
        contacto = input("Ingrese el contacto del proveedor: ")
        
        cursor.execute("INSERT INTO proveedores (nombre, contacto, estado) VALUES (?, ?, 1)",
        (nombre, contacto))
        conexion.commit()
        print("Proveedor agregado correctamente.")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

def modificar_proveedor():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    
    try:
        listar_proveedores()
        id_prov_mod = int(input("Ingrese el id del proveedor a modificar: "))
        cursor.execute("SELECT * FROM proveedores WHERE id_proveedor == ? AND estado == 1", (id_prov_mod,))
        proveedor = cursor.fetchone()
        
        if proveedor is None:
            print("No existe un proveedor activo con ese ID.")
            return
        
        print("\nProveedor encontrado:")
        print(f"ID: {proveedor[0]}")
        print(f"Nombre: {proveedor[1]}")
        print(f"Contacto: {proveedor[2]}")
        
        nombre_actual = proveedor[1]
        contacto_actual = proveedor[2]
        
        print("\n¿Qué atributos desea modificar?")
        print("1. Nombre")
        print("2. Contacto")
        print("0. Cancelar")
        
        opciones = input("Ingrese los números de las opciones separados por comas (ej: 1,2): ")
        opciones = [op.strip() for op in opciones.split(',') if op.strip().isdigit()]
        
        if not opciones or '0' in opciones:
            print("Modificación cancelada.")
            return
            
        for op in opciones:
            if op == '1':
                nuevo_nombre = input(f"Ingrese nuevo nombre (actual: {nombre_actual}): ")
                if not es_vacia(nuevo_nombre):
                    nombre_actual = nuevo_nombre
            elif op == '2':
                nuevo_contacto = input(f"Ingrese nuevo contacto (actual: {contacto_actual}): ")
                contacto_actual = nuevo_contacto
        
        print("\nResumen de cambios:")
        print(f"Nombre: {nombre_actual}")
        print(f"Contacto: {contacto_actual}")
        
        if confirmarFN():
            cursor.execute("UPDATE proveedores SET nombre=?, contacto=? WHERE id_proveedor=?",
                (nombre_actual, contacto_actual, id_prov_mod))
            conexion.commit()
            print("Proveedor modificado exitosamente.")
        else:
            print("Modificación cancelada.")
            
    except ValueError:
        print("Error: Ingrese un ID válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

def desactivar_proveedor():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    
    try:
        listar_proveedores()
        id_prov_des = int(input("Ingrese el id del proveedor a desactivar: "))
        cursor.execute("SELECT * FROM proveedores WHERE id_proveedor == ? AND estado == 1", (id_prov_des,))
        proveedor = cursor.fetchone()
        
        if proveedor is None:
            print("No existe un proveedor activo con ese ID.")
            return
        
        print("\nProveedor encontrado:")
        print(f"ID: {proveedor[0]}")
        print(f"Nombre: {proveedor[1]}")
        print(f"Contacto: {proveedor[2]}")
        
        if confirmarFN():
            cursor.execute("UPDATE proveedores SET estado=? WHERE id_proveedor=?",
                (0, id_prov_des))
            conexion.commit()
            print("El proveedor ha sido desactivado exitosamente.")
        else:
            print("Operación cancelada.")
            
    except ValueError:
        print("Error: Ingrese un ID válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

def listar_proveedores():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT * FROM proveedores WHERE estado == 1")
        resultados = cursor.fetchall()
        
        if not resultados:
            print("No hay proveedores activos.")
            return
            
        print("\n=== LISTADO DE PROVEEDORES ===")
        print(f"{'ID':<5} {'Nombre':<20} {'Contacto':<20}")
        print("-" * 45)
        for proveedor in resultados:
            print(f"{proveedor[0]:<5} {proveedor[1]:<20} {proveedor[2]:<20}")
            
        return resultados
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conexion.close()

# Funciones de registros
def registrar_compra():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    
    try:
        # Mostrar productos disponibles
        productos = listar_productos()
        if not productos:
            print("No hay productos disponibles para comprar.")
            return
            
        # Mostrar proveedores disponibles
        proveedores = listar_proveedores()
        if not proveedores:
            print("No hay proveedores disponibles.")
            return
            
        id_producto = int(input("\nIngrese el ID del producto: "))
        id_proveedor = int(input("Ingrese el ID del proveedor: "))
        cantidad = int(input("Ingrese la cantidad comprada: "))
        precio_unitario = float(input("Ingrese el precio unitario de compra: "))
        
        # Verificar que el producto existe
        cursor.execute("SELECT * FROM productos WHERE id_producto = ? AND estado = 1", (id_producto,))
        producto = cursor.fetchone()
        
        if producto is None:
            print("ERROR: Producto no encontrado o inactivo.")
            return
        
        # Verificar que el proveedor existe
        cursor.execute("SELECT * FROM proveedores WHERE id_proveedor = ? AND estado = 1", (id_proveedor,))
        proveedor = cursor.fetchone()
        
        if proveedor is None:
            print("ERROR: Proveedor no encontrado o inactivo.")
            return
        
        if cantidad <= 0:
            print("ERROR: La cantidad debe ser mayor a 0.")
            return
            
        if precio_unitario <= 0:
            print("ERROR: El precio unitario debe ser mayor a 0.")
            return
        
        precio_total = cantidad * precio_unitario
        fecha_compra = datetime.datetime.now()
        
        print("\n=== RESUMEN DE COMPRA ===")
        print(f"Producto: {producto[1]}")
        print(f"Proveedor: {proveedor[1]}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio unitario: ${precio_unitario:.2f}")
        print(f"Precio total: ${precio_total:.2f}")
        
        if confirmarFN():
            # Registrar la compra
            cursor.execute("INSERT INTO compras (id_producto, id_proveedor, cantidad, precio_unitario, precio_total, fecha_compra) VALUES (?, ?, ?, ?, ?, ?)",
                         (id_producto, id_proveedor, cantidad, precio_unitario, precio_total, fecha_compra))
            
            # Actualizar stock del producto
            nuevo_stock = producto[4] + cantidad
            cursor.execute("UPDATE productos SET stock = ? WHERE id_producto = ?", (nuevo_stock, id_producto))
            
            conexion.commit()
            print("\nCompra registrada exitosamente y stock actualizado.")
        else:
            print("\nCompra cancelada.")
            
    except ValueError:
        print("ERROR: Debe ingresar valores numéricos válidos.")
    except Exception as e:
        print(f"ERROR inesperado: {e}")
    finally:
        conexion.close()

def registrar_venta():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    
    try:
        # Mostrar productos disponibles
        productos = listar_productos()
        if not productos:
            print("No hay productos disponibles para vender.")
            return
            
        id_producto = int(input("\nIngrese el ID del producto: "))
        cantidad = int(input("Ingrese la cantidad vendida: "))
        
        # Verificar que el producto existe y tiene stock suficiente
        cursor.execute("SELECT * FROM productos WHERE id_producto = ? AND estado = 1", (id_producto,))
        producto = cursor.fetchone()
        
        if producto is None:
            print("ERROR: Producto no encontrado o inactivo.")
            return
        
        if cantidad <= 0:
            print("ERROR: La cantidad debe ser mayor a 0.")
            return
            
        if producto[4] < cantidad:
            print(f"ERROR: Stock insuficiente. Stock disponible: {producto[4]}")
            return
        
        precio_unitario = producto[3]  # Precio del producto
        precio_total = cantidad * precio_unitario
        fecha_venta = datetime.datetime.now()
        
        print("\n=== RESUMEN DE VENTA ===")
        print(f"Producto: {producto[1]}")
        print(f"Cantidad: {cantidad}")
        print(f"Precio unitario: ${precio_unitario:.2f}")
        print(f"Precio total: ${precio_total:.2f}")
        
        if confirmarFN():
            # Registrar la venta
            cursor.execute("INSERT INTO ventas (id_producto, cantidad, precio_unitario, precio_total, fecha_venta) VALUES (?, ?, ?, ?, ?)",
                         (id_producto, cantidad, precio_unitario, precio_total, fecha_venta))
            
            # Actualizar stock del producto
            nuevo_stock = producto[4] - cantidad
            cursor.execute("UPDATE productos SET stock = ? WHERE id_producto = ?", (nuevo_stock, id_producto))
            
            conexion.commit()
            print("\nVenta registrada exitosamente y stock actualizado.")
        else:
            print("\nVenta cancelada.")
            
    except ValueError:
        print("ERROR: Debe ingresar valores numéricos válidos.")
    except Exception as e:
        print(f"ERROR inesperado: {e}")
    finally:
        conexion.close()

def mostrar_registros_compras():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    
    try:
        cursor.execute("""
            SELECT c.id_compra, p.nombre, pr.nombre, c.cantidad, c.precio_unitario, c.precio_total, c.fecha_compra
            FROM compras c
            JOIN productos p ON c.id_producto = p.id_producto
            JOIN proveedores pr ON c.id_proveedor = pr.id_proveedor
            WHERE c.estado = 1
            ORDER BY c.fecha_compra DESC
        """)
        
        resultados = cursor.fetchall()
        
        if not resultados:
            print("\nNo hay registros de compras.")
            return
            
        print("\n=== REGISTROS DE COMPRAS ===")
        print(f"{'ID':<5} {'Producto':<20} {'Proveedor':<20} {'Cant':<8} {'P.Unit':<10} {'P.Total':<10} {'Fecha':<20}")
        print("-" * 95)
        for registro in resultados:
            fecha = registro[6].split('.')[0]  # Remover microsegundos
            print(f"{registro[0]:<5} {registro[1]:<20} {registro[2]:<20} {registro[3]:<8} ${registro[4]:<9.2f} ${registro[5]:<9.2f} {fecha:<20}")
    except Exception as e:
        print(f"ERROR inesperado: {e}")
    finally:
        conexion.close()

def mostrar_registros_ventas():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    
    try:
        cursor.execute("""
            SELECT v.id_venta, p.nombre, v.cantidad, v.precio_unitario, v.precio_total, v.fecha_venta
            FROM ventas v
            JOIN productos p ON v.id_producto = p.id_producto
            WHERE v.estado = 1
            ORDER BY v.fecha_venta DESC
        """)
        
        resultados = cursor.fetchall()
        
        if not resultados:
            print("\nNo hay registros de ventas.")
            return
            
        print("\n=== REGISTROS DE VENTAS ===")
        print(f"{'ID':<5} {'Producto':<20} {'Cant':<8} {'P.Unit':<10} {'P.Total':<10} {'Fecha':<20}")
        print("-" * 75)
        for registro in resultados:
            fecha = registro[5].split('.')[0]  # Remover microsegundos
            print(f"{registro[0]:<5} {registro[1]:<20} {registro[2]:<8} ${registro[3]:<9.2f} ${registro[4]:<9.2f} {fecha:<20}")
    except Exception as e:
        print(f"ERROR inesperado: {e}")
    finally:
        conexion.close()

def exportar_registros():
    conexion = sqlite3.connect("kiosko.db")
    cursor = conexion.cursor()
    
    try:
        print("\n¿Qué registros desea exportar?")
        print("1. Compras")
        print("2. Ventas")
        print("3. Ambos")
        print("0. Cancelar")
        
        opcion = int(input("Ingrese su opción: "))
        if opcion == 0:
            print("Exportación cancelada.")
            return
            
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if opcion == 1:
            # Exportar compras
            cursor.execute("""
                SELECT c.id_compra, p.nombre, pr.nombre, c.cantidad, c.precio_unitario, c.precio_total, c.fecha_compra
                FROM compras c
                JOIN productos p ON c.id_producto = p.id_producto
                JOIN proveedores pr ON c.id_proveedor = pr.id_proveedor
                WHERE c.estado = 1
                ORDER BY c.fecha_compra DESC
            """)
            
            resultados = cursor.fetchall()
            if not resultados:
                print("No hay registros de compras para exportar.")
                return
                
            nombre_archivo = f"registros_compras_{fecha_actual}.txt"
            
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write("=== REGISTROS DE COMPRAS ===\n")
                archivo.write(f"{'ID':<5} {'Producto':<20} {'Proveedor':<20} {'Cant':<8} {'P.Unit':<10} {'P.Total':<10} {'Fecha':<20}\n")
                archivo.write("-" * 95 + "\n")
                
                for registro in resultados:
                    fecha = registro[6].split('.')[0]
                    archivo.write(f"{registro[0]:<5} {registro[1]:<20} {registro[2]:<20} {registro[3]:<8} ${registro[4]:<9.2f} ${registro[5]:<9.2f} {fecha:<20}\n")
            
            print(f"\nRegistros de compras exportados a: {nombre_archivo}")
            
        elif opcion == 2:
            # Exportar ventas
            cursor.execute("""
                SELECT v.id_venta, p.nombre, v.cantidad, v.precio_unitario, v.precio_total, v.fecha_venta
                FROM ventas v
                JOIN productos p ON v.id_producto = p.id_producto
                WHERE v.estado = 1
                ORDER BY v.fecha_venta DESC
            """)
            
            resultados = cursor.fetchall()
            if not resultados:
                print("No hay registros de ventas para exportar.")
                return
                
            nombre_archivo = f"registros_ventas_{fecha_actual}.txt"
            
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write("=== REGISTROS DE VENTAS ===\n")
                archivo.write(f"{'ID':<5} {'Producto':<20} {'Cant':<8} {'P.Unit':<10} {'P.Total':<10} {'Fecha':<20}\n")
                archivo.write("-" * 75 + "\n")
                
                for registro in resultados:
                    fecha = registro[5].split('.')[0]
                    archivo.write(f"{registro[0]:<5} {registro[1]:<20} {registro[2]:<8} ${registro[3]:<9.2f} ${registro[4]:<9.2f} {fecha:<20}\n")
            
            print(f"\nRegistros de ventas exportados a: {nombre_archivo}")
            
        elif opcion == 3:
            # Exportar ambos
            nombre_archivo = f"registros_completos_{fecha_actual}.txt"
            
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                # Compras
                cursor.execute("""
                    SELECT c.id_compra, p.nombre, pr.nombre, c.cantidad, c.precio_unitario, c.precio_total, c.fecha_compra
                    FROM compras c
                    JOIN productos p ON c.id_producto = p.id_producto
                    JOIN proveedores pr ON c.id_proveedor = pr.id_proveedor
                    WHERE c.estado = 1
                    ORDER BY c.fecha_compra DESC
                """)
                
                resultados_compras = cursor.fetchall()
                
                archivo.write("=== REGISTROS DE COMPRAS ===\n")
                archivo.write(f"{'ID':<5} {'Producto':<20} {'Proveedor':<20} {'Cant':<8} {'P.Unit':<10} {'P.Total':<10} {'Fecha':<20}\n")
                archivo.write("-" * 95 + "\n")
                
                for registro in resultados_compras:
                    fecha = registro[6].split('.')[0]
                    archivo.write(f"{registro[0]:<5} {registro[1]:<20} {registro[2]:<20} {registro[3]:<8} ${registro[4]:<9.2f} ${registro[5]:<9.2f} {fecha:<20}\n")
                
                archivo.write("\n\n")
                
                # Ventas
                cursor.execute("""
                    SELECT v.id_venta, p.nombre, v.cantidad, v.precio_unitario, v.precio_total, v.fecha_venta
                    FROM ventas v
                    JOIN productos p ON v.id_producto = p.id_producto
                    WHERE v.estado = 1
                    ORDER BY v.fecha_venta DESC
                """)
                
                resultados_ventas = cursor.fetchall()
                
                archivo.write("=== REGISTROS DE VENTAS ===\n")
                archivo.write(f"{'ID':<5} {'Producto':<20} {'Cant':<8} {'P.Unit':<10} {'P.Total':<10} {'Fecha':<20}\n")
                archivo.write("-" * 75 + "\n")
                
                for registro in resultados_ventas:
                    fecha = registro[5].split('.')[0]
                    archivo.write(f"{registro[0]:<5} {registro[1]:<20} {registro[2]:<8} ${registro[3]:<9.2f} ${registro[4]:<9.2f} {fecha:<20}\n")
            
            print(f"\nRegistros completos exportados a: {nombre_archivo}")
            
        else:
            print("Opción inválida.")
            
    except ValueError:
        print("ERROR: Ingrese una opción válida (1, 2 o 3).")
    except Exception as e:
        print(f"ERROR inesperado al exportar: {e}")
    finally:
        conexion.close()

# Función de menu principal
def menu_principal():
    while True:
        print("\n<--- Menú principal ---> \n1. Productos\n2. Proveedores\n3. Registros\n4. Salir")
        try:
            op_usuario = int(input("Ingrese el número de la opción que desea: "))
            
            if op_usuario == 1:
                # Menú de productos
                while True:
                    mostrar_menus(1)
                    try:
                        op_producto = int(input("Ingrese su opción: "))
                        if op_producto == 1:
                            agregar_producto()
                        elif op_producto == 2:
                            modificar_producto()
                        elif op_producto == 3:
                            desactivar_productos()
                        elif op_producto == 4:
                            listar_productos()
                        elif op_producto == 5:
                            break
                        else:
                            print("Opción inválida. Intente nuevamente.")
                    except ValueError:
                        print("ERROR: Debe ingresar un número entero.")
                        
            elif op_usuario == 2:
                # Menú de proveedores
                while True:
                    mostrar_menus(2)
                    try:
                        op_proveedor = int(input("Ingrese su opción: "))
                        if op_proveedor == 1:
                            agregar_proveedor()
                        elif op_proveedor == 2:
                            modificar_proveedor()
                        elif op_proveedor == 3:
                            desactivar_proveedor()
                        elif op_proveedor == 4:
                            listar_proveedores()
                        elif op_proveedor == 5:
                            break
                        else:
                            print("Opción inválida. Intente nuevamente.")
                    except ValueError:
                        print("ERROR: Debe ingresar un número entero.")
                        
            elif op_usuario == 3:
                # Menú de registros
                while True:
                    mostrar_menus(3)
                    try:
                        op_registro = int(input("Ingrese su opción: "))
                        if op_registro == 1:
                            registrar_compra()
                        elif op_registro == 2:
                            registrar_venta()
                        elif op_registro == 3:
                            mostrar_registros_compras()
                        elif op_registro == 4:
                            mostrar_registros_ventas()
                        elif op_registro == 5:
                            exportar_registros()
                        elif op_registro == 6:
                            break
                        else:
                            print("Opción inválida. Intente nuevamente.")
                    except ValueError:
                        print("ERROR: Debe ingresar un número entero.")
                        
            elif op_usuario == 4:
                print("\nGracias por usar el sistema. ¡Hasta luego!")
                break
            else:
                print("Opción inválida. Intente nuevamente.")
                
        except ValueError:
            print("ERROR: Debe ingresar un número entero. Intente nuevamente.")

# Ejecutar el programa
print("=== SISTEMA DE GESTIÓN DE KIOSKO ===")
menu_principal()
