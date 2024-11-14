from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import urllib
import pyodbc
from datetime import datetime

app = Flask(__name__)

# Configuración de la conexión a SQL Server
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=BDVENTAS;"
    "UID=CRUDBD;"
    "PWD=123;"
)

# Crear una conexión a la base de datos
def get_db_connection():
    return pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost\\SQLEXPRESS;DATABASE=BDVENTAS;UID=CRUDBD;PWD=123")

@app.route('/')
def inicio():
    return render_template('base.html')
#------------------------
# INICIO
#------------------------
#vista1
@app.route('/productos_proveedor')
def productos_proveedor():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Comprobar si la vista existe
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = 'VISTAPRODUCTOSPROVEEDOR'")
    result = cursor.fetchone()

    if result:
        # Si la vista existe, obtenemos los datos de la vista
        cursor.execute("SELECT * FROM VISTAPRODUCTOSPROVEEDOR")
        rows = cursor.fetchall()
        return render_template('productos_proveedor.html', rows=rows)
    else:
        return "Vista 'VISTAPRODUCTOSPROVEEDOR' no encontrada.", 404

#vista 2
@app.route('/ventas_por_vendedor')
def ventas_por_vendedor():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM VENTAS_POR_VENDEDOR')
    ventas = cursor.fetchall()
    conn.close()
    return render_template('ventas_por_vendedor.html', ventas=ventas)

#procedimiento
@app.route('/detalle_facturaproce')
def detalle_factura():
    num_fac = request.args.get('num_fac')  # Captura el número de factura de la URL
    detalle_factura = []

    if num_fac:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("EXEC dbo.ObtenerDetalleFactura2 @num_fac = ?", num_fac)
            detalle_factura = cursor.fetchall()
        except Exception as e:
            print("Error ejecutando el procedimiento almacenado:", e)
        finally:
            cursor.close()
            conn.close()

    return render_template('detalle_factura.html', detalle_factura=detalle_factura, num_fac=num_fac)

#funcion
@app.route('/productos_por_distrito')
def productos_por_distrito():
    codigo_distrito = request.args.get('codigoDistrito')  # Captura el código de distrito de la URL
    productos_list = []

    if codigo_distrito:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM dbo.ProductosPorDistrito(?)", codigo_distrito)
            productos_list = cursor.fetchall()
        except Exception as e:
            print("Error ejecutando la función:", e)
        finally:
            cursor.close()
            conn.close()

    return render_template('productos_por_distrito.html', productos_list=productos_list, codigo_distrito=codigo_distrito)
#------------------------------------------
# CLIENTE
#------------------------------------------

# Obtener todos los clientes
@app.route('/clientes', methods=['GET'])
def mostrar_clientes():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM CLIENTE")
    clientes = cursor.fetchall()
    connection.close()
    return render_template('CLIENTE/index.html', cliente_list=clientes)


# Actualizar un cliente
@app.route('/clientes/<cod_cli>/actualizar', methods=['GET', 'POST'])
def actualizar_cliente_view(cod_cli):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM CLIENTE WHERE COD_CLI = ?", (cod_cli,))
    cliente = cursor.fetchone()
    
    if not cliente:
        connection.close()
        return jsonify({"error": "Cliente no encontrado"}), 404

    if request.method == 'POST':
        # Obtener datos del formulario
        data = request.form
        cursor.execute("""
            UPDATE CLIENTE SET 
                RSO_CLI = ?, 
                DIR_CLI = ?, 
                TLF_CLI = ?, 
                RUC_CLI = ?, 
                COD_DIS = ?, 
                FEC_REG = ?, 
                TIP_CLI = ?, 
                CON_CLI = ? 
            WHERE COD_CLI = ?
        """, (
            data['RSO_CLI'],
            data['DIR_CLI'],
            data['TLF_CLI'],
            data.get('RUC_CLI'),
            data['COD_DIS'],
            datetime.strptime(data['FEC_REG'], '%Y-%m-%d'),
            data['TIP_CLI'],
            data['CON_CLI'],
            cod_cli
        ))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_clientes'))

    connection.close()
    return render_template('CLIENTE/update_cliente.html', cliente=cliente)


# Registrar un nuevo cliente
@app.route('/clientes/registrar', methods=['GET', 'POST'])
def registrar_cliente():
    if request.method == 'POST':
        # Obtener datos del formulario
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO CLIENTE (COD_CLI, RSO_CLI, DIR_CLI, TLF_CLI, RUC_CLI, COD_DIS, FEC_REG, TIP_CLI, CON_CLI) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['COD_CLI'],
            data['RSO_CLI'],
            data['DIR_CLI'],
            data['TLF_CLI'],
            data.get('RUC_CLI'),
            data['COD_DIS'],
            datetime.strptime(data['FEC_REG'], '%Y-%m-%d'),
            data['TIP_CLI'],
            data['CON_CLI']
        ))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_clientes'))

    return render_template('CLIENTE/form.html')


# Eliminar un cliente
@app.route('/clientes/<cod_cli>/eliminar', methods=['GET', 'POST'])
def eliminar_cliente(cod_cli):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM CLIENTE WHERE COD_CLI = ?", (cod_cli,))
    cliente = cursor.fetchone()

    if not cliente:
        connection.close()
        return jsonify({"error": "Cliente no encontrado"}), 404

    if request.method == 'POST':
        # Eliminar el cliente
        cursor.execute("DELETE FROM CLIENTE WHERE COD_CLI = ?", (cod_cli,))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_clientes'))

    connection.close()
    return render_template('CLIENTE/delete_cliente.html', cliente=cliente)


#------------------------------------------
#ABASTECIMIENTO
#------------------------------------------
# Ruta para mostrar todos los registros de abastecimiento
@app.route('/abastecimiento', methods=['GET'])
def mostrar_abastecimiento():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ABASTECIMIENTO")
    abastecimientos = cursor.fetchall()
    connection.close()
    return render_template('ABASTECIMIENTO/index_abas.html', abastecimiento_list=abastecimientos)

# Ruta para mostrar el formulario de registro de un nuevo abastecimiento
@app.route('/abastecimiento/registrar', methods=['GET', 'POST'])
def registrar_abastecimiento():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO ABASTECIMIENTO (COD_PRV, COD_PRO, PRE_ABA)
            VALUES (?, ?, ?)
        """, (data['COD_PRV'], data['COD_PRO'], data['PRE_ABA']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_abastecimiento'))

    return render_template('ABASTECIMIENTO/form_abas.html')

# Ruta para mostrar y procesar el formulario de actualización de un abastecimiento
@app.route('/abastecimiento/<cod_prv>/<cod_pro>/actualizar', methods=['GET', 'POST'])
def actualizar_abastecimiento(cod_prv, cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM ABASTECIMIENTO WHERE COD_PRV = ? AND COD_PRO = ?
    """, (cod_prv, cod_pro))
    abastecimiento = cursor.fetchone()

    if not abastecimiento:
        connection.close()
        return jsonify({"error": "Abastecimiento no encontrado"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE ABASTECIMIENTO
            SET PRE_ABA = ?
            WHERE COD_PRV = ? AND COD_PRO = ?
        """, (data['PRE_ABA'], cod_prv, cod_pro))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_abastecimiento'))

    connection.close()
    return render_template('ABASTECIMIENTO/update_abas.html', abastecimiento=abastecimiento)

# Ruta para mostrar la confirmación de eliminación de un abastecimiento
@app.route('/abastecimiento/<cod_prv>/<cod_pro>/eliminar', methods=['GET', 'POST'])
def eliminar_abastecimiento(cod_prv, cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM ABASTECIMIENTO WHERE COD_PRV = ? AND COD_PRO = ?
    """, (cod_prv, cod_pro))
    abastecimiento = cursor.fetchone()

    if not abastecimiento:
        connection.close()
        return jsonify({"error": "Abastecimiento no encontrado"}), 404

    if request.method == 'POST':
        cursor.execute("""
            DELETE FROM ABASTECIMIENTO WHERE COD_PRV = ? AND COD_PRO = ?
        """, (cod_prv, cod_pro))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_abastecimiento'))

    connection.close()
    return render_template('ABASTECIMIENTO/delete_abas.html', abastecimiento=abastecimiento)


#-------------------------------------------
#DETALLE COMPRA
#------------------------------------------
# Ruta para mostrar todos los detalles de compra
@app.route('/detalle_compra', methods=['GET'])
def mostrar_detalle_compra():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DETALLE_COMPRA")
    detalles = cursor.fetchall()
    connection.close()
    return render_template('DETALLE_COMPRA/index_detcom.html', detalle_list=detalles)

# Ruta para mostrar el formulario de registro de un nuevo detalle de compra
@app.route('/detalle_compra/registrar', methods=['GET', 'POST'])
def registrar_detalle_compra():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO DETALLE_COMPRA (NUM_OCO, COD_PRO, CAN_DET)
            VALUES (?, ?, ?)
        """, (data['NUM_OCO'], data['COD_PRO'], data['CAN_DET']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_detalle_compra'))

    return render_template('DETALLE_COMPRA/form_detcom.html')

# Ruta para mostrar y procesar el formulario de actualización de un detalle de compra
@app.route('/detalle_compra/<num_oco>/<cod_pro>/actualizar', methods=['GET', 'POST'])
def actualizar_detalle_compra(num_oco, cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM DETALLE_COMPRA WHERE NUM_OCO = ? AND COD_PRO = ?
    """, (num_oco, cod_pro))
    detalle = cursor.fetchone()

    if not detalle:
        connection.close()
        return jsonify({"error": "Detalle no encontrado"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE DETALLE_COMPRA
            SET CAN_DET = ?
            WHERE NUM_OCO = ? AND COD_PRO = ?
        """, (data['CAN_DET'], num_oco, cod_pro))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_detalle_compra'))

    connection.close()
    return render_template('DETALLE_COMPRA/update_detcom.html', detalle=detalle)

# Ruta para mostrar la confirmación de eliminación de un detalle de compra
@app.route('/detalle_compra/<num_oco>/<cod_pro>/eliminar', methods=['GET', 'POST'])
def eliminar_detalle_compra(num_oco, cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM DETALLE_COMPRA WHERE NUM_OCO = ? AND COD_PRO = ?
    """, (num_oco, cod_pro))
    detalle = cursor.fetchone()

    if not detalle:
        connection.close()
        return jsonify({"error": "Detalle no encontrado"}), 404

    if request.method == 'POST':
        cursor.execute("""
            DELETE FROM DETALLE_COMPRA WHERE NUM_OCO = ? AND COD_PRO = ?
        """, (num_oco, cod_pro))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_detalle_compra'))

    connection.close()
    return render_template('DETALLE_COMPRA/delete_detcom.html', detalle=detalle)


#-------------------------------------------
#DETALLE FACTURA
#------------------------------------------
# Ruta para mostrar todos los detalles de las facturas
@app.route('/detalle_factura', methods=['GET'])
def mostrar_detalle_factura():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DETALLE_FACTURA")
    detalles = cursor.fetchall()
    connection.close()
    return render_template('DETALLE_FACTURA/index_detfac.html', detalle_list=detalles)

# Ruta para mostrar el formulario de registro de un nuevo detalle de factura
@app.route('/detalle_factura/registrar', methods=['GET', 'POST'])
def registrar_detalle_factura():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO DETALLE_FACTURA (NUM_FAC, COD_PRO, CAN_VEN, PRE_VEN)
            VALUES (?, ?, ?, ?)
        """, (data['NUM_FAC'], data['COD_PRO'], data['CAN_VEN'], data['PRE_VEN']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_detalle_factura'))

    return render_template('DETALLE_FACTURA/form_detfac.html')

# Ruta para mostrar y procesar el formulario de actualización de un detalle de factura
@app.route('/detalle_factura/<num_fac>/<cod_pro>/actualizar', methods=['GET', 'POST'])
def actualizar_detalle_factura(num_fac, cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DETALLE_FACTURA WHERE NUM_FAC = ? AND COD_PRO = ?", (num_fac, cod_pro))
    detalle = cursor.fetchone()

    if not detalle:
        connection.close()
        return jsonify({"error": "Detalle no encontrado"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE DETALLE_FACTURA
            SET CAN_VEN = ?, PRE_VEN = ?
            WHERE NUM_FAC = ? AND COD_PRO = ?
        """, (data['CAN_VEN'], data['PRE_VEN'], num_fac, cod_pro))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_detalle_factura'))
    connection.close()
    return render_template('DETALLE_FACTURA/update_detfac.html', detalle=detalle)

# Ruta para mostrar la confirmación de eliminación de un detalle de factura
@app.route('/detalle_factura/<num_fac>/<cod_pro>/eliminar', methods=['GET', 'POST'])
def eliminar_detalle_factura(num_fac, cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DETALLE_FACTURA WHERE NUM_FAC = ? AND COD_PRO = ?", (num_fac, cod_pro))
    detalle = cursor.fetchone()

    if not detalle:
        connection.close()
        return jsonify({"error": "Detalle no encontrado"}), 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM DETALLE_FACTURA WHERE NUM_FAC = ? AND COD_PRO = ?", (num_fac, cod_pro))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_detalle_factura'))
    
    connection.close()
    return render_template('DETALLE_FACTURA/delete_detfac.html', detalle=detalle)

#-----------------------------------------
# DISTRITO CRUD
#-----------------------------------------

@app.route('/distritos', methods=['GET'])
def mostrar_distritos():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DISTRITO")
    distritos = cursor.fetchall()
    connection.close()
    return render_template('DISTRITO/index_dis.html', distrito_list=distritos)

# Ruta para mostrar el formulario de registro de un nuevo distrito
@app.route('/distritos/registrar', methods=['GET', 'POST'])
def registrar_distrito():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO DISTRITO (COD_DIS, NOM_DIS) VALUES (?, ?)", (data['COD_DIS'], data['NOM_DIS']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_distritos'))
    return render_template('DISTRITO/form_dis.html')

# Ruta para mostrar y procesar el formulario de actualización de un distrito
@app.route('/distritos/<cod_dis>/actualizar', methods=['GET', 'POST'])
def actualizar_distrito(cod_dis):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DISTRITO WHERE COD_DIS = ?", (cod_dis,))
    distrito = cursor.fetchone()

    if not distrito:
        connection.close()
        return jsonify({"error": "Distrito no encontrado"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("UPDATE DISTRITO SET NOM_DIS = ? WHERE COD_DIS = ?", (data['NOM_DIS'], cod_dis))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_distritos'))
    
    connection.close()
    return render_template('DISTRITO/update_dis.html', distrito=distrito)

# Ruta para mostrar la confirmación de eliminación de dstrito
@app.route('/distritos/<cod_dis>/eliminar', methods=['GET', 'POST'])
def eliminar_distrito(cod_dis):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DISTRITO WHERE COD_DIS = ?", (cod_dis,))
    distrito = cursor.fetchone()

    if not distrito:
        connection.close()
        return jsonify({"error": "Distrito no encontrado"}), 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM DISTRITO WHERE COD_DIS = ?", (cod_dis,))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_distritos'))

    connection.close()
    return render_template('DISTRITO/delete_dis.html', distrito=distrito)


#-----------------------------------------
#FACTURA
#-----------------------------------------
# Ruta para mostrar todas las facturas
@app.route('/facturas', methods=['GET'])
def mostrar_facturas():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM FACTURA")
    facturas = cursor.fetchall()
    connection.close()
    return render_template('FACTURA/index_fac.html', factura_list=facturas)

# Ruta para mostrar el formulario de registro de una nueva factura
@app.route('/facturas/registrar', methods=['GET', 'POST'])
def registrar_factura():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO FACTURA (NUM_FAC, FEC_FAC, COD_CLI, FEC_CAN, EST_FAC, COD_VEN, POR_IGV)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['NUM_FAC'], data['FEC_FAC'], data['COD_CLI'], data['FEC_CAN'], data['EST_FAC'], data['COD_VEN'], data['POR_IGV']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_facturas'))
    return render_template('FACTURA/form_fac.html')

# Ruta para mostrar y procesar el formulario de actualización de una factura
@app.route('/facturas/<num_fac>/actualizar', methods=['GET', 'POST'])
def actualizar_factura(num_fac):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM FACTURA WHERE NUM_FAC = ?", (num_fac,))
    factura = cursor.fetchone()

    if not factura:
        connection.close()
        return jsonify({"error": "Factura no encontrada"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE FACTURA
            SET FEC_FAC = ?, COD_CLI = ?, FEC_CAN = ?, EST_FAC = ?, COD_VEN = ?, POR_IGV = ?
            WHERE NUM_FAC = ?
        """, (data['FEC_FAC'], data['COD_CLI'], data['FEC_CAN'], data['EST_FAC'], data['COD_VEN'], data['POR_IGV'], num_fac))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_facturas'))

    connection.close()
    return render_template('FACTURA/update_fac.html', factura=factura)

# Ruta para mostrar la confirmación de eliminación de una factura
@app.route('/facturas/<num_fac>/eliminar', methods=['GET', 'POST'])
def eliminar_factura(num_fac):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM FACTURA WHERE NUM_FAC = ?", (num_fac,))
    factura = cursor.fetchone()

    if not factura:
        connection.close()
        return jsonify({"error": "Factura no encontrada"}), 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM FACTURA WHERE NUM_FAC = ?", (num_fac,))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_facturas'))

    connection.close()
    return render_template('FACTURA/delete_fac.html', factura=factura)

#----------------------------------------
#ORDEN COMPRA
#----------------------------------------
# Ruta para mostrar todas las órdenes de compra
@app.route('/ordenes-compra', methods=['GET'])
def mostrar_ordenes_compra():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ORDEN_COMPRA")
    ordenes_compra = cursor.fetchall()
    connection.close()
    return render_template('ORDEN_COMPRA/index_oc.html', orden_compra_list=ordenes_compra)

# Ruta para mostrar el formulario de registro de una nueva orden de compra
@app.route('/ordenes-compra/registrar', methods=['GET', 'POST'])
def registrar_orden_compra():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO ORDEN_COMPRA (NUM_OCO, FEC_OCO, COD_PRV, FAT_OCO, EST_OCO)
            VALUES (?, ?, ?, ?, ?)
        """, (data['NUM_OCO'], data['FEC_OCO'], data['COD_PRV'], data['FAT_OCO'], data['EST_OCO']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_ordenes_compra'))

    return render_template('ORDEN_COMPRA/form_oc.html')

# Ruta para mostrar y procesar el formulario de actualización de una orden de compra
@app.route('/ordenes-compra/<num_oco>/actualizar', methods=['GET', 'POST'])
def actualizar_orden_compra(num_oco):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ORDEN_COMPRA WHERE NUM_OCO = ?", (num_oco,))
    orden_compra = cursor.fetchone()

    if not orden_compra:
        connection.close()
        return jsonify({"error": "Orden de compra no encontrada"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE ORDEN_COMPRA
            SET FEC_OCO = ?, COD_PRV = ?, FAT_OCO = ?, EST_OCO = ?
            WHERE NUM_OCO = ?
        """, (data['FEC_OCO'], data['COD_PRV'], data['FAT_OCO'], data['EST_OCO'], num_oco))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_ordenes_compra'))


    return render_template('ORDEN_COMPRA/update_oc.html', orden_compra=orden_compra)

# Ruta para mostrar la confirmación de eliminación de una orden de compra
@app.route('/ordenes-compra/<num_oco>/eliminar', methods=['GET', 'POST'])
def eliminar_orden_compra(num_oco):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ORDEN_COMPRA WHERE NUM_OCO = ?", (num_oco,))
    orden_compra = cursor.fetchone()

    if not orden_compra:
        connection.close()
        return jsonify({"error": "Orden de compra no encontrada"}), 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM ORDEN_COMPRA WHERE NUM_OCO = ?", (num_oco,))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_ordenes_compra'))

    connection.close()
    return render_template('ORDEN_COMPRA/delete_oc.html', orden_compra=orden_compra)


#------------------------------------------
#PRODUCTO
#-----------------------------------------
# Ruta para mostrar todos los productos
@app.route('/productos', methods=['GET'])
def mostrar_productos():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PRODUCTO")
    productos = cursor.fetchall()
    return render_template('PRODUCTO/index_pro.html', producto_list=productos)

# Ruta para mostrar el formulario de registro de un nuevo producto
@app.route('/productos/registrar', methods=['GET', 'POST'])
def registrar_producto():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO PRODUCTO (COD_PRO, DES_PRO, PRE_PRO, SAC_PRO, SMI_PRO, UNI_PRO, LIN_PRO, IMP_PRO)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (data['COD_PRO'], data['DES_PRO'], data['PRE_PRO'], data['SAC_PRO'], data['SMI_PRO'], data['UNI_PRO'], data['LIN_PRO'], data['IMP_PRO']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_productos'))

    return render_template('PRODUCTO/form_pro.html')

# Ruta para mostrar y procesar el formulario de actualización de un producto
@app.route('/productos/<cod_pro>/actualizar', methods=['GET', 'POST'])
def actualizar_producto(cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PRODUCTO WHERE COD_PRO = ?", (cod_pro,))
    producto = cursor.fetchone()

    if not producto:
        connection.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE PRODUCTO
            SET DES_PRO = ?, PRE_PRO = ?, SAC_PRO = ?, SMI_PRO = ?, UNI_PRO = ?, LIN_PRO = ?, IMP_PRO = ?
            WHERE COD_PRO = ?
        """, (data['DES_PRO'], data['PRE_PRO'], data['SAC_PRO'], data['SMI_PRO'], data['UNI_PRO'], data['LIN_PRO'], data['IMP_PRO'], cod_pro))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_productos'))

    connection.close()
    return render_template('PRODUCTO/update_pro.html', producto=producto)

# Ruta para mostrar la confirmación de eliminación de un producto
@app.route('/productos/<cod_pro>/eliminar', methods=['GET', 'POST'])
def eliminar_producto(cod_pro):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PRODUCTO WHERE COD_PRO = ?", (cod_pro,))
    producto = cursor.fetchone()

    if not producto:
        connection.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM PRODUCTO WHERE COD_PRO = ?", (cod_pro,))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_productos'))

    connection.close()
    return render_template('PRODUCTO/delete_pro.html', producto=producto)


#-----------------
#PROVEEDOR
#---------------------
#Ruta para mostrar todos los proveedores
@app.route('/proveedores', methods=['GET'])
def mostrar_proveedores():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PROVEEDOR")
    proveedores = cursor.fetchall()
    connection.close()
    return render_template('PROVEEDOR/index_prov.html', proveedor_list=proveedores)

# Ruta para mostrar el formulario de registro de un nuevo proveedor
@app.route('/proveedores/registrar', methods=['GET', 'POST'])
def registrar_proveedor():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO PROVEEDOR (COD_PRV, RSO_PRV, DIR_PRV, TEL_PRV, COD_DIS, REP_PRV)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['COD_PRV'], data['RSO_PRV'], data['DIR_PRV'], data.get('TEL_PRV'), data['COD_DIS'], data['REP_PRV']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_proveedores'))

    return render_template('PROVEEDOR/form_prov.html')

# Ruta para mostrar y procesar el formulario de actualización de un proveedor
@app.route('/proveedores/<cod_prv>/actualizar', methods=['GET', 'POST'])
def actualizar_proveedor(cod_prv):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PROVEEDOR WHERE COD_PRV = ?", (cod_prv,))
    proveedor = cursor.fetchone()

    if not proveedor:
        connection.close()
        return jsonify({"error": "Proveedor no encontrado"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE PROVEEDOR
            SET RSO_PRV = ?, DIR_PRV = ?, TEL_PRV = ?, COD_DIS = ?, REP_PRV = ?
            WHERE COD_PRV = ?
        """, (data['RSO_PRV'], data['DIR_PRV'], data.get('TEL_PRV'), data['COD_DIS'], data['REP_PRV'], cod_prv))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_proveedores'))

    connection.close()
    return render_template('PROVEEDOR/update_prov.html', proveedor=proveedor)

# Ruta para mostrar la confirmación de eliminación de un proveedor
@app.route('/proveedores/<cod_prv>/eliminar', methods=['GET', 'POST'])
def eliminar_proveedor(cod_prv):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PROVEEDOR WHERE COD_PRV = ?", (cod_prv,))
    proveedor = cursor.fetchone()

    if not proveedor:
        connection.close()
        return jsonify({"error": "Proveedor no encontrado"}), 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM PROVEEDOR WHERE COD_PRV = ?", (cod_prv,))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_proveedores'))

    connection.close()
    return render_template('PROVEEDOR/delete_prov.html', proveedor=proveedor)

#------------------------------------------------------------------
#VENDEDOR
#-----------------------------------------------------------------

# Ruta para mostrar todos los vendedores
@app.route('/vendedores', methods=['GET'])
def mostrar_vendedores():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM VENDEDOR")
    vendedores = cursor.fetchall()
    connection.close()
    return render_template('VENDEDOR/index_vend.html', vendedor_list=vendedores)

# Ruta para mostrar el formulario de registro de un nuevo vendedor
@app.route('/vendedores/registrar', methods=['GET', 'POST'])
def registrar_vendedor():
    if request.method == 'POST':
        data = request.form
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO VENDEDOR (COD_VEN, NOM_VEN, APE_VEN, SUE_VEN, FIN_VEN, TIP_VEN, COD_DIS)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['COD_VEN'], data['NOM_VEN'], data['APE_VEN'], data['SUE_VEN'], data['FIN_VEN'], data['TIP_VEN'], data['COD_DIS']))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_vendedores'))

    return render_template('VENDEDOR/form_vend.html')

# Ruta para mostrar y procesar el formulario de actualización de un vendedor
@app.route('/vendedores/<cod_ven>/actualizar', methods=['GET', 'POST'])
def actualizar_vendedor(cod_ven):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM VENDEDOR WHERE COD_VEN = ?", (cod_ven,))
    vendedor = cursor.fetchone()

    if not vendedor:
        connection.close()
        return jsonify({"error": "Vendedor no encontrado"}), 404

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE VENDEDOR
            SET NOM_VEN = ?, APE_VEN = ?, SUE_VEN = ?, FIN_VEN = ?, TIP_VEN = ?, COD_DIS = ?
            WHERE COD_VEN = ?
        """, (data['NOM_VEN'], data['APE_VEN'], data['SUE_VEN'], data['FIN_VEN'], data['TIP_VEN'], data['COD_DIS'], cod_ven))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_vendedores'))

    connection.close()
    return render_template('VENDEDOR/update_vend.html', vendedor=vendedor)

# Ruta para mostrar la confirmación de eliminación de un vendedor
@app.route('/vendedores/<cod_ven>/eliminar', methods=['GET', 'POST'])
def eliminar_vendedor(cod_ven):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM VENDEDOR WHERE COD_VEN = ?", (cod_ven,))
    vendedor = cursor.fetchone()

    if not vendedor:
        connection.close()
        return jsonify({"error": "Vendedor no encontrado"}), 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM VENDEDOR WHERE COD_VEN = ?", (cod_ven,))
        connection.commit()
        connection.close()
        return redirect(url_for('mostrar_vendedores'))

    connection.close()
    return render_template('VENDEDOR/delete_vend.html', vendedor=vendedor)


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)



