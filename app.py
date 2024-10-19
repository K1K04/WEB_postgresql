from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave_muy_insegura')

@app.route('/')
def inicio():
    error = session.pop('error', None) 
    return render_template('index.html', error=error)

@app.route('/datos', methods=["POST"])
def datos():
    # Obtener los datos del formulario
    usuario = request.form.get("usuario")
    contrasenia = request.form.get("contrasenia")
    basedatos = request.form.get("basedatos")

    if not usuario or not contrasenia or not basedatos:
        session['error'] = "Faltan datos del formulario"
        return redirect(url_for('inicio'))
    
    try:
        session['usuario'] = usuario
        session['contrasenia'] = contrasenia
        session['basedatos'] = basedatos

        db = psycopg2.connect(host="192.168.122.196", user=usuario, password=contrasenia, database=basedatos)

        cursor = db.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tablas = cursor.fetchall()

        return render_template('datos.html', tablas=tablas, conexion="bien")

    except psycopg2.Error:
        session['error'] = "Error de conexión a la base de datos"
        return redirect(url_for('inicio'))

@app.route('/tablas/<tabla>')
def detalle(tabla):
    usuario = session.get('usuario')
    contrasenia = session.get('contrasenia')
    basedatos = session.get('basedatos')

    if not usuario or not contrasenia or not basedatos:
        return redirect(url_for('inicio'))

    try:
        db = psycopg2.connect(host="192.168.122.196", user=usuario, password=contrasenia, database=basedatos)
        cursor = db.cursor()

        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{tabla}'")
        columnas = cursor.fetchall()

        cursor.execute(f"SELECT * FROM {tabla}")
        filas = cursor.fetchall()

        return render_template('tablas.html', tabla=tabla, columnas=columnas, filas=filas)

    except psycopg2.Error as e:
        return f"Error al conectar o consultar: {str(e)}"

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)