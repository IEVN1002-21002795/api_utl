from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
 
 
 
from config import config
 
app=Flask(__name__)
 
con=MySQL(app)
 
@app.route("/alumnos",methods=['GET'])
def lista_alumnos():
    try:
        cursor=con.connection.cursor()
        sql='select * from alumnos order by nombre ASC'
        cursor.execute(sql)
        datos=cursor.fetchall()
        alumnos=[]
        for fila in datos:
            alumno={'matricula':fila[0],'nombre':fila[1],'apaterno':fila[2],'amaterno':fila[3],'correo':fila[4]}
            alumnos.append(alumno)
            print(alumnos)
        return jsonify({'alumnos':alumnos,'mensaje':'Lista de alumnos','exito':True})
    except Exception as ex:
        return jsonify({"message": "Error al conectar a la base de datos {}".format(ex),'exito':False})
 
 
def leer_alumno_bd(matricula):
    try:
        cursor=con.connection.cursor()
        sql='select * from alumnos where matricula={0}'.format(matricula)
        cursor.execute(sql)
        datos=cursor.fetchone()
        if datos!=None:
            alumno={'matricula':datos[0],'nombre':datos[1],'apaterno':datos[2],'amaterno':datos[3],'correo':datos[4]}
            return alumno
    except Exception as ex:
        return jsonify({"message": "Error al conectar a la base de datos {}"})
 
@app.route("/alumnos/<mat>",methods=['GET'])
def leer_alumno(mat):
    try:
        alumno=leer_alumno_bd(mat)
        if alumno!=None:
            return jsonify({'alumnos':alumno,'mensaje':'Alumno encontrado','exito':True})
    except Exception as ex:
        return jsonify({'mensaje':'Alumno no encontrado','exito':False})
   
 
@app.route("/alumnos",methods=['POST'])
def registro_alumnos():
    try:
        alumno=leer_alumno_bd(request.json['matricula'])
        if alumno!=None:
            return jsonify({'mensaje':'Alumno ya existe','exito':False})
        else:
            cursor=con.connection.cursor()
            sql='''INSERT INTO alumnos (matricula, nombre, apaterno, amaterno, correo)
                values('{0}','{1}','{2}','{3}','{4}')'''.format(request.json['matricula'],request.json['nombre'],request.json['apaterno'],request.json['amaterno'],request.json['correo'])
            cursor.execute(sql)
            con.connection.commit()
            return jsonify({'mensaje':'Alumno agregado','exito':True})
    except Exception as ex:
        return jsonify({"message": "Error al conectar a la base de datos {}".format(ex),'exito':False})
 
 
def pagina_no_encontrada(error):
    return "<h1>La pagina que estas buscando no existe</h1>",400
 
if __name__=="__main__":
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run(host='0.0.0.0', port=5000)