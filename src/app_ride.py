from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pymysql
from datetime import datetime


app_ride = Flask(__name__)
CORS(app_ride, resources={r"/*": {"origins": "http://localhost:4200"}})

db_config = {
    'host': 'localhost',
    'user': 'diego',
    'password': '1234',
    'db': 'ride'
}


def conectar_db():
    return pymysql.connect(**db_config)

# ------------------------------------------------------------------------------------------

@app_ride.route('/login', methods=['POST'])
def login():
    datos = request.json
    usuario = datos.get('usuario') 
    password = datos.get('password') 

    if not usuario or not password:
        return jsonify({"message": "Usuario y contraseña son requeridos"}), 400

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE usuario=%s AND password=%s"
        cursor.execute(consulta, (usuario, password))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado:
            return jsonify({"message": "Login exitoso", "user": usuario})
        else:
            return jsonify({"message": "Usuario o contraseña incorrectos"}), 401
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error en la base de datos", "error": str(e)}), 500

# ------------------------------------------------------------------------------------------

@app_ride.route('/usuarios', methods=['POST'])
def agregar_usuario():
    datos = request.json
    campos_requeridos = ['id', 'nombre', 'apellidos', 'correo', 'tipo_usuario', 'status', 'fecha_registro', 'password']

    for campo in campos_requeridos:
        if not datos.get(campo):
            return jsonify({"message": f"El campo {campo} es requerido"}), 400

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        consulta = """
            INSERT INTO usuarios_ride (id, nombre, apellidos, correo, tipo_usuario, status, fecha_registro, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            consulta,
            (datos['id'], datos['nombre'], datos['apellidos'], datos['correo'], datos['tipo_usuario'], datos['status'], datos['fecha_registro'], datos['password'])
        )
        conexion.commit()
        conexion.close()

        return jsonify({"message": "Usuario agregado correctamente"}), 201
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al agregar usuario", "error": str(e)}), 500
# ------------------------------------------------------------------------------------------

@app_ride.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    filtro = request.args.get('filtro', None) 

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        if filtro:
            consulta = """
                SELECT id, nombre, apellidos, correo, tipo_usuario, password, status, fecha_registro 
                FROM usuarios_ride 
                WHERE id = %s OR nombre LIKE %s OR apellidos LIKE %s
                ORDER BY id DESC
            """
            cursor.execute(consulta, (filtro, f"%{filtro}%", f"%{filtro}%"))
        else:
            consulta = """
                SELECT id, nombre, apellidos, correo, tipo_usuario, password, status, fecha_registro 
                FROM usuarios_ride 
                ORDER BY id DESC
            """
            cursor.execute(consulta)

        resultados = cursor.fetchall()
        conexion.close()

        return jsonify(resultados), 200
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al obtener usuarios", "error": str(e)}), 500

# ------------------------------------------------------------------------------------------
@app_ride.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    datos = request.json
    campos_requeridos = ['id', 'nombre', 'apellidos', 'correo', 'tipo_usuario', 'status', 'fecha_registro', 'password']

    for campo in campos_requeridos:
        if not datos.get(campo):
            return jsonify({"message": f"El campo {campo} es requerido"}), 400

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        consulta = """
            UPDATE usuarios_ride 
            SET id = %s, nombre = %s, apellidos = %s, correo = %s, tipo_usuario = %s, status = %s, fecha_registro = %s, password = %s
            WHERE id = %s
        """
        cursor.execute(
            consulta,
            (datos['id'], datos['nombre'], datos['apellidos'], datos['correo'], datos['tipo_usuario'], datos['status'], datos['fecha_registro'], datos['password'], id)
        )
        conexion.commit()
        conexion.close()

        return jsonify({"message": "Usuario actualizado correctamente"}), 200
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al actualizar usuario", "error": str(e)}), 500
# ------------------------------------------------------------------------------------------

@app_ride.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        consulta = "DELETE FROM usuarios_ride WHERE id = %s"
        cursor.execute(consulta, (id,))
        conexion.commit()
        conexion.close()

        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al eliminar usuario", "error": str(e)}), 500

# ------------------------------------------------------------------------------------------

@app_ride.route('/dashboard', methods=['GET'])
def obtener_dashboard():
    conexion = conectar_db()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Total de usuarios
    cursor.execute("SELECT COUNT(*) AS total_usuarios FROM usuarios_ride;")
    total_usuarios = cursor.fetchone()

    # Usuarios por tipo
    cursor.execute("SELECT tipo_usuario, COUNT(*) AS total FROM usuarios_ride GROUP BY tipo_usuario;")
    usuarios_por_tipo = cursor.fetchall()

    # Usuarios activos e inactivos
    cursor.execute("SELECT status, COUNT(*) AS total FROM usuarios_ride GROUP BY status;")
    usuarios_status = cursor.fetchall()

    # Usuarios registrados hoy
    cursor.execute("SELECT COUNT(*) AS registrados_hoy FROM usuarios_ride WHERE DATE(fecha_registro) = CURDATE();")
    registrados_hoy = cursor.fetchone()

    # Ganancia del día
    cursor.execute("SELECT IFNULL(SUM(comision_ride), 0) AS ganancia_dia FROM viajes WHERE DATE(fecha) = CURDATE();")
    ganancia_dia = cursor.fetchone()

    # Ganancia mensual
    cursor.execute("""
        SELECT IFNULL(SUM(comision_ride), 0) AS ganancia_mensual 
        FROM viajes 
        WHERE MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE());
    """)
    ganancia_mensual = cursor.fetchone()

    conexion.close()

    return jsonify({
        "total_usuarios": total_usuarios['total_usuarios'],
        "usuarios_por_tipo": usuarios_por_tipo,
        "usuarios_status": usuarios_status,
        "registrados_hoy": registrados_hoy['registrados_hoy'],
        "ganancia_dia": float(ganancia_dia['ganancia_dia']),
        "ganancia_mensual": float(ganancia_mensual['ganancia_mensual'])
    })

# ------------------------------------------------------------------------------------------


#Ojo ----------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# Ruta para obtener usuarios
@app_ride.route('/usuarios_admn', methods=['GET'])
def obtener_usuarios_admn():
    filtro = request.args.get('filtro', None)  # Obtener filtro de la query string

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        if filtro:
            consulta = """
                SELECT id, nombre, apellidos, usuario, password, rol 
                FROM usuarios 
                WHERE id = %s OR nombre LIKE %s OR apellidos LIKE %s
                ORDER BY id DESC
            """
            cursor.execute(consulta, (filtro, f"%{filtro}%", f"%{filtro}%"))
        else:
            consulta = "SELECT id, nombre, apellidos, usuario, password, rol FROM usuarios ORDER BY id DESC"
            cursor.execute(consulta)

        resultados = cursor.fetchall()
        conexion.close()

        return jsonify(resultados), 200
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al obtener usuarios", "error": str(e)}), 500

# ------------------------------------------------------------------------------------------

@app_ride.route('/usuarios_admn', methods=['POST'])
def agregar_usuario_admn():
    datos = request.json

    campos_requeridos = ['nombre', 'apellidos', 'usuario', 'password', 'rol']
    for campo in campos_requeridos:
        if not datos.get(campo):
            return jsonify({"message": f"El campo {campo} es requerido"}), 400

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        consulta = """
            INSERT INTO usuarios (nombre, apellidos, usuario, password, rol) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            consulta,
            (datos['nombre'], datos['apellidos'], datos['usuario'], datos['password'], datos['rol'])
        )
        conexion.commit()
        conexion.close()

        return jsonify({"message": "Usuario agregado correctamente"}), 201
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al agregar usuario", "error": str(e)}), 500

# ------------------------------------------------------------------------------------------

@app_ride.route('/usuarios_admn/<int:id>', methods=['PUT'])
def actualizar_usuario_admn(id):
    datos = request.json

    
    campos_requeridos = ['nombre', 'apellidos', 'usuario', 'password', 'rol']
    for campo in campos_requeridos:
        if not datos.get(campo):
            return jsonify({"message": f"El campo {campo} es requerido"}), 400

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        consulta = """
            UPDATE usuarios 
            SET nombre = %s, apellidos = %s, usuario = %s, password = %s, rol = %s 
            WHERE id = %s
        """
        cursor.execute(
            consulta,
            (datos['nombre'], datos['apellidos'], datos['usuario'], datos['password'], datos['rol'], id)
        )
        conexion.commit()
        conexion.close()

        return jsonify({"message": "Usuario actualizado correctamente"}), 200
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al actualizar usuario", "error": str(e)}), 500

# ------------------------------------------------------------------------------------------

@app_ride.route('/usuarios_admn/<int:id>', methods=['DELETE'])
def eliminar_usuario_admn(id):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        consulta = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(consulta, (id,))
        conexion.commit()
        conexion.close()

        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    except pymysql.MySQLError as e:
        return jsonify({"message": "Error al eliminar usuario", "error": str(e)}), 500




if __name__ == '__main__':
    app_ride.run(debug=True)

