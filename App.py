from flask import Flask, request, jsonify, render_template, redirect, url_for
from conexion import get_connection

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('base.html')

# CREATE (Crear)
@app.route('/materiales/nuevo', methods=['GET', 'POST'])
def crear_material():
    if request.method == 'POST':
        id_material = request.form['id_material']
        tipo = request.form['tipo']
        nombre_material = request.form['nombre_material']
        costo = request.form['costo']
        descripcion = request.form['descripcion']
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Material_Religioso 
                (id_material, tipo, nombre_material, costo, descripcion) 
                VALUES (?, ?, ?, ?, ?)
            """, (id_material, tipo, nombre_material, costo, descripcion))
            conn.commit()
            conn.close()
            return redirect(url_for('mostrar_materiales'))
        except Exception as e:
            return f"Error al crear material: {e}", 500
    return render_template('MATERIAL/nuevo.html')

# READ (Leer/Mostrar)
@app.route('/materiales', methods=['GET'])
def mostrar_materiales():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Material_Religioso")
        materiales = cursor.fetchall()
        conn.close()
        return render_template('MATERIAL/index.html', material_list=materiales)
    except Exception as e:
        return f"Error al recuperar materiales: {e}", 500

# UPDATE (Actualizar)
@app.route('/materiales/editar/<string:id_material>', methods=['GET', 'POST'])
def editar_material(id_material):
    if request.method == 'POST':
        tipo = request.form['tipo']
        nombre_material = request.form['nombre_material']
        costo = request.form['costo']
        descripcion = request.form['descripcion']
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Material_Religioso 
                SET tipo=?, nombre_material=?, costo=?, descripcion=?
                WHERE id_material=?
            """, (tipo, nombre_material, costo, descripcion, id_material))
            conn.commit()
            conn.close()
            return redirect(url_for('mostrar_materiales'))
        except Exception as e:
            return f"Error al actualizar material: {e}", 500
    
    # Obtener datos para editar
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Material_Religioso WHERE id_material=?", (id_material,))
        material = cursor.fetchone()
        conn.close()
        return render_template('MATERIAL/editar.html', material=material)
    except Exception as e:
        return f"Error al obtener material: {e}", 500

# DELETE (Eliminar)
@app.route('/materiales/eliminar/<string:id_material>', methods=['GET'])
def eliminar_material(id_material):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Material_Religioso WHERE id_material=?", (id_material,))
        conn.commit()
        conn.close()
        return redirect(url_for('mostrar_materiales'))
    except Exception as e:
        return f"Error al eliminar material: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)