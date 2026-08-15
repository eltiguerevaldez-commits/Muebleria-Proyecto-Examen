"""
Modulo de conexion a MySQL.
Ajusta host / usuario / password segun tu instalacion de MySQL.
"""
import mysql.connector
from mysql.connector import Error

CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "23092006",          # <-- coloca aqui tu password de MySQL
    "database": "caribbean_furniture"
}


def obtener_conexion():
    """Devuelve una nueva conexion a la base de datos, o None si falla."""
    try:
        conexion = mysql.connector.connect(**CONFIG)
        return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
