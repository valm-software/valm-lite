from collections import defaultdict
from flask import Flask, json, render_template, request, redirect, url_for, flash, session, g, jsonify,send_from_directory,send_file
from flask_session import Session
from datetime import timedelta
from functools import wraps
from database import init_app
from models.Clientes import db, Cliente
from models.VentasEncabezados import db, VentaEncabezado
from models.Gastos import db, Gasto
from models.Usuarios import db, Usuario
from models.Productos import db, Producto
from models.VentasDetalles import db, VentaDetalle
from models.VentasEncabezados import db, VentaEncabezado
from models.CompromisoDePagos import db, CompromisoDePago
from models.MediosDePagos import db, MedioDePago
from models.Cuotas import db, Cuota
from models.Usuarios import db, Usuario
from werkzeug.utils import secure_filename
import os
from urllib.parse import unquote
from datetime import datetime , time
import io
import pandas as pd
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_  # Asegúrate de que or_ esté importado aquí

import locale 

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configura la localización a español de Argentina
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')

# Definir un filtro personalizado para formatear números como moneda sin decimales
def format_currency(value):
    # Formatear el valor con separadores de miles y sin decimales
    formatted_value = "${:,.0f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted_value

# Registrar el filtro con Jinja2
app.jinja_env.filters['currency'] = format_currency


# Configurar la sesión para que caduque después de 2 horas de inactividad
app.config['SESSION_TYPE'] = 'filesystem'
#app.config['SESSION_FILE_DIR'] = '/home/soporte/valm-lite/flask-session'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

Session(app)


# Configura la conexión a la base de datos desde database.py
init_app(app)


# Datos de ejemplo: usuarios y permisos
usuarios = {
    'victor.lm': {
        'IdUsuario': 1,
        'password': 'victor.lm',
        'permisos': {
            'tarjetas': ['crear', 'consultar'],
            'clientes': ['crear', 'consultar'],
            'cobros': ['crear', 'consultar', 'modificar'],
            'gastos': ['crear', 'consultar'],
            'inicio': ['crear', 'consultar'],
            'admin': ['crear', 'consultar'],
            'buscador': ['crear', 'consultar']
        }
    },
    'fray.lm': {
        'IdUsuario': 2,
        'password': 'fray.lm',
        'permisos': {
            'tarjetas': ['crear', 'consultar'],
            'clientes': ['crear', 'consultar'],
            'cobros': ['crear', 'consultar', 'modificar'],
            'gastos': ['crear', 'consultar'],
            'inicio': ['crear', 'consultar'],
            'admin': ['crear', 'consultar'],
            'buscador': ['crear', 'consultar']
        }
    },
    'parra.pa': {
        'IdUsuario': 3,
        'password': 'parra.pa',
        'permisos': {
            'tarjetas': ['crear', 'consultar'],
            'clientes': ['crear', 'consultar'],
            'cobros': ['crear', 'consultar', 'modificar'],
            'gastos': ['crear', 'consultar'],
            'inicio': ['crear', 'consultar'],
            'admin': ['crear', 'consultar'],
            'buscador': ['crear', 'consultar']
        }
    }
}


# Decorador para requerir inicio de sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Página de inicio
@app.route('/')
def inicio():
    # Verificar si el usuario ya está autenticado
    if 'usuario' in session:
        return redirect(url_for('menu', usuario=session['usuario']))
    
    return render_template('bienvenida.html')

# Página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verificar si el usuario ya está autenticado
    if 'usuario' in session:
        return redirect(url_for('menu', usuario=session['usuario']))

    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        if usuario in usuarios and usuarios[usuario]['password'] == password:
            session['usuario'] = usuario
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('inicio_web', usuario=usuario))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Cierra la sesión del usuario
    flash('Has cerrado sesión', 'success')  # Opcional: muestra un mensaje de éxito
    return redirect(url_for('login'))  # Redirige al usuario a la página de inicio de sesión


# Página principal con menú
@app.route('/menu/<usuario>')
@login_required
def menu(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."

    permisos = usuarios.get(usuario, {}).get('permisos', {})
    return render_template('menu.html', permisos=permisos, usuario=usuario)

# ... Resto de las rutas para las secciones como tarjetas, clientes, cobros, etc.

# Submenús para tarjetas y clientes
@app.route('/menu/tarjetas/<usuario>')
@login_required
def tarjetas(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosTarjetas = usuarios.get(usuario, {}).get('permisos', {}).get('tarjetas', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'tarjetas' in permisosTarjetas:
        return render_template('tarjetas.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."

@app.route('/menu/clientes/<usuario>')
@login_required
def clientes(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosClientes = usuarios.get(usuario, {}).get('permisos', {}).get('clientes', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'clientes' in permisosClientes:
        return render_template('clientes.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."

@app.route('/menu/cobros/<usuario>')
@login_required
def cobros(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosCobros = usuarios.get(usuario, {}).get('permisos', {}).get('cobros', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'cobros' in permisosCobros:
        return render_template('cobros.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."

# Submenús para crear y consultar tarjetas/clientes



@app.route('/menu/tarjetas/crear/<usuario>', methods=['GET', 'POST'])  # Permitir métodos GET y POST
@login_required
def crear_tarjeta(usuario):
   
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    
    permisosCrear = usuarios.get(usuario, {}).get('permisos', {}).get('tarjetas', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    
    if 'crear' not in permisosCrear:
        return "No tienes permisos para ver esta página."
    
    id_usuario = usuarios.get(usuario, {}).get('IdUsuario', None)
    accion = None  # Inicializar la variable antes del bloque if
    if request.method == 'POST':
        data = request.get_json()

        print("Datos recibidos:", data)
        
        accion = data.get('accion', None)
        
        if accion == 'crear_cliente':
            try:
                    nuevo_cliente = Cliente(
                        Nombres=data['Nombres'],
                        Apellidos=data['Apellidos'],
                        DNI=data['DNI'],
                        Telefono1=data['Telefono1'],
                        Telefono2=data['Telefono2'],
                        Telefono3=data['Telefono3'],
                        Direccion=data['Direccion'],
                        Ubicacion=data['Ubicacion'],
                        Nota=data['Nota']
                    )
                    db.session.add(nuevo_cliente)
                    db.session.commit()
                    return jsonify(message="Cliente creado con éxito"), 200  # Respuesta JSON exitosa
            except Exception as e:
                db.session.rollback()
                return jsonify(message=f"Error al crear cliente: {str(e)}"), 400  # Respuesta JSON de error
        
        elif accion == 'crear_encabezado':
            try:
                nuevo_encabezado = VentaEncabezado(
                    ImporteVenta=data['ImporteVenta'],
                    ImporteInicial=data['ImporteInicial'],
                    NumCuotas=data['NumCuotas'],
                    IdCompPago = data.get('tipoCompromiso'),
                    IdCliente = data.get('clienteId'),
                   # Fventa=data['Fventa'],
                    NumTarjeta=data['NumTarjeta'],
                    FProxCuota=data['FProxCuota'],
                    FVenta=data.get('FVenta'),
                    Ciudad=data['Ciudad'],
                    Responsable=data['Responsable'],
                    Comentario=data['Comentario'],
                    IdUsuario=id_usuario  # Suponiendo que tienes un campo para el usuario en VentasEncabezados
                )
                db.session.add(nuevo_encabezado)
                db.session.commit()
                return jsonify(message="Encabezado creado con éxito", encabezadoId=nuevo_encabezado.Id), 200
            except Exception as e:
                db.session.rollback()
                return jsonify(message=f"Error al crear encabezado: {str(e)}"), 400

        elif accion == 'crear_detalle':
            try:
                nuevo_detalle = VentaDetalle(
                    IdProducto=data['productoId'],  # Suponiendo que tienes un campo para el producto
                    Cantidad=data['cantidad'],
                    IdVentaEncabezado=data['encabezadoId']  # ID del encabezado creado anteriormente
                )
                db.session.add(nuevo_detalle)
                db.session.commit()
                return jsonify(message="Detalle creado con éxito"), 200
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}") 
                return jsonify(message=f"Error al crear detalle:  {str(e)}"), 400
                

    return render_template('crear_tarjeta.html', permisos=permisos, usuario=usuario)



@app.route('/get_next_num_tarjeta', methods=['GET'])
@login_required
def get_next_num_tarjeta():
    query = text('SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = :database AND TABLE_NAME = "VentasEncabezados"')
    result = db.session.execute(query, {'database': db.engine.url.database}).fetchone()
    next_id = result[0] if result else None
    return jsonify({'next_id': next_id})


@app.route('/menu/tarjetas/consultar/<usuario>', methods=['GET', 'POST'])
@login_required
def consultar_tarjeta(usuario):
    resultados_encabezado = None
    resultados_productos = None
    resultados_cuotas = None
    
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('cobros', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    
    if request.method == 'POST':
        id_venta = request.form['id_venta']  # Obtener el valor del formulario (ajustar el nombre del campo)
        
        try:
            # Ejecutar el procedimiento almacenado getTarjetaEncabezado
            cursor_encabezado = db.session.connection().connection.cursor()
            cursor_encabezado.callproc('getTarjetaEncabezado', [id_venta])
            resultados_encabezado = [dict(zip([column[0] for column in cursor_encabezado.description], row)) for row in cursor_encabezado.fetchall()]
            cursor_encabezado.close()
            print('resultados_encabezado: ', resultados_encabezado)            
            
            # Ejecutar el procedimiento almacenado getTarjetaProductos
            cursor_productos = db.session.connection().connection.cursor()
            cursor_productos.callproc('getTarjetaProductos', [id_venta])
            resultados_productos = [dict(zip([column[0] for column in cursor_productos.description], row)) for row in cursor_productos.fetchall()]
            cursor_productos.close()
            print('resultados_productos: ', resultados_productos)
            
            # Ejecutar el procedimiento almacenado getTarjetaCuotas
            cursor_cuotas = db.session.connection().connection.cursor()
            cursor_cuotas.callproc('getTarjetaCuotas', [id_venta])
            resultados_cuotas = [dict(zip([column[0] for column in cursor_cuotas.description], row)) for row in cursor_cuotas.fetchall()]
            cursor_cuotas.close()
            print('resultados_cuotas: ', resultados_cuotas)

            # Confirmar los cambios (en caso de que los procedimientos hayan modificado la base de datos)
            db.session.commit()
        except Exception as e:
            # Manejar cualquier error que ocurra durante la ejecución de los procedimientos
            print("Error al ejecutar los procedimientos:", e)
            db.session.rollback()  # Revertir cualquier cambio en caso de error

    if 'consultar' in permisosConsultar:
        return render_template('consultar_tarjeta.html', permisos=permisos, usuario=usuario, 
                               resultados_encabezado=resultados_encabezado,
                               resultados_productos=resultados_productos,
                               resultados_cuotas=resultados_cuotas)
    else:
        return "No tienes permisos para ver esta página."








@app.route('/menu/clientes/crear/<usuario>')
@login_required
def crear_cliente(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosCrear = usuarios.get(usuario, {}).get('permisos', {}).get('clientes', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'crear' in permisosCrear:
        return render_template('crear_cliente.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."



# @app.route('/menu/clientes/consultar/<usuario>')
# @login_required
# def consultar_cliente(usuario):
#     if usuario != session['usuario']:
#         return "Acceso denegado: No puedes acceder a esta página."
#     permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('clientes', [])
#     permisos = usuarios.get(usuario, {}).get('permisos', {})
#     if 'consultar' in permisosConsultar:
#         return render_template('consultar_cliente.html', permisos=permisos, usuario=usuario)
#     else:
#         return "No tienes permisos para ver esta página."


@app.route('/menu/clientes/consultar/<usuario>')
@login_required
def consultar_cliente(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('clientes', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'consultar' in permisosConsultar:
        # Realiza la consulta a la base de datos para obtener los clientes
        clientes = Cliente.query.all()  # Esto supone que tienes un modelo Cliente

        # Renderiza la plantilla y pasa los clientes como argumento
        return render_template('consultar_cliente.html', permisos=permisos, usuario=usuario, clientes=clientes)
    else:
        return "No tienes permisos para ver esta página."




@app.route('/menu/cobros/crear/<usuario>', methods=['GET', 'POST'])
@login_required
def crear_cobro(usuario):
    id_usuario = usuarios.get(usuario, {}).get('IdUsuario', None)
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosCrear = usuarios.get(usuario, {}).get('permisos', {}).get('cobros', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    
    if 'crear' not in permisosCrear:
        return "No tienes permisos para ver esta página."

    if request.method == 'GET':
        return render_template('crear_cobro.html', permisos=permisos, usuario=usuario)

    elif request.method == 'POST':
        try:
            # Obtener datos desde el cliente
            medioPago = int(request.form['medioPago'])
            fechaPago = request.form['fechaPago']
            numCuota = int(request.form['numCuota'])
            abono = float(request.form['abono'])
            liquidado = int(request.form['liquidado'])
            calculo = float(request.form['calculo'])
            IdVentaEncabezado = int(request.form['IdVentaEncabezado'])
            fechaproxpago = request.form['fechaproxpago']  # Asumiendo que es un entero
            venta_encabezado = VentaEncabezado.query.get(IdVentaEncabezado)
            if venta_encabezado:
                venta_encabezado.FProxCuota = fechaproxpago  # Actualiza el campo
                db.session.commit()  # Guarda los cambios
            else:
                return jsonify({'message': 'IdVentaEncabezado no encontrado'}), 404
            
            # Crear el objeto Cuota (Cobro en tu caso)
            nueva_cuota = Cuota(
                IdMedioDePago=medioPago,
                FechaPago=fechaPago,
                NumCuota=numCuota,
                Abono=abono,
                Liquidado = liquidado,
                IdUsuario=id_usuario,
                Saldo=calculo,
                IdVentaEncabezado=IdVentaEncabezado  # Asumiendo que tienes un campo para esto
            )
            
            # Añadir y confirmar
            db.session.add(nueva_cuota)
            db.session.commit()

            return jsonify({'message': 'Cobro creado con éxito'}), 200

        except Exception as e:
            db.session.rollback()  # Deshacer los cambios en caso de error
            app.logger.error(f"Error desconocido: {str(e)}")
            return jsonify({'message': f'Error al crear el cobro: {str(e)}'}), 500


from decimal import Decimal
@app.route('/menu/cobros/consultar/<usuario>', methods=['GET', 'POST'])
@login_required
def consultar_cobro(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."

    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('tarjetas', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})

    if request.method == 'POST':
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']

        cursor_informeco = db.session.connection().connection.cursor()
        cursor_informeco.callproc('InfoPagosxRangoFechas', [fecha_inicio, fecha_fin])
        resultados_informe = [dict(zip([column[0] for column in cursor_informeco.description], row)) for row in cursor_informeco.fetchall()]
        cursor_informeco.close()

        if resultados_informe:  # Verificar si hay resultados
            # Convertir valores de las columnas 'abono' y 'saldo' a enteros
            for row in resultados_informe:
                if row['Abono']:
                    row['Abono'] = int(row['Abono'])
                else:
                    row['Abono'] = 0

                if row['Saldo']:
                    row['Saldo'] = int(row['Saldo'])
                else:
                    row['Saldo'] = 0

                # Ajustar el detalle según el producto
                if 'PRESTAMO' not in row['Producto']:
                    row['Detalle'] = ''  # Quitar el detalle si no es un préstamo
                else:
                # Eliminar puntos y comas del detalle si es un préstamo
                    if row['Detalle']:
                        row['Detalle'] = row['Detalle'].replace('.', '').replace(',', '')
                        
            # Calcular la suma de los abonos que contienen la palabra 'préstamo' de mobiplaz`
            suma_prestamos_mobiplaz = sum(row['Abono'] for row in resultados_informe if row['Producto'] == 'PRESTAMOS')

            # Calcular la suma de los abonos que contienen la palabra 'préstamos `parra'
            suma_prestamos_parra=  sum(row['Abono'] for row in resultados_informe if row['Producto'] == 'PRESTAMOS PARRA')

            # Calcular la suma de los abonos que contienen la palabra 'préstamo'
            suma_prestamos = sum(row['Abono'] for row in resultados_informe if 'PRESTAMOS PARRA' in row['Producto'] or 'PRESTAMOS' in row['Producto'])

            # Calcular la suma de los demás abonos
            suma_otros_abonos = sum(row['Abono'] for row in resultados_informe if 'PRESTAMOS PARRA' not in row['Producto'] and 'PRESTAMOS' not in row['Producto'])

            # Calcular la suma total de todos los abonos
            suma_abonos_total = sum(row['Abono'] for row in resultados_informe)
            



            session['resultados_informe'] = resultados_informe
            return render_template('consultar_cobro.html', permisos=permisos, 
                                                           usuario=usuario, 
                                                           resultado_procedimiento=resultados_informe, 
                                                           suma_prestamos_mobiplaz=suma_prestamos_mobiplaz,
                                                           suma_prestamos_parra=suma_prestamos_parra,
                                                           suma_prestamos=suma_prestamos, 
                                                           suma_otros_abonos=suma_otros_abonos, 
                                                           suma_abonos_total=suma_abonos_total)
        else:
            return render_template('consultar_cobro.html', permisos=permisos, usuario=usuario, no_resultados=True)

    return render_template('consultar_cobro.html', permisos=permisos, usuario=usuario)

@app.route('/menu/cobros/modificar/<usuario>', methods=['GET', 'POST'])
@login_required
def cuotas_dia(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    today = datetime.today().date()
    max_date = today + timedelta(days=15)
    selected_date = request.form.get('selected_date') or request.args.get('selected_date') or today
    
    # cuotas = db.session.query(VentaEncabezado, Cliente, Producto.Nombre).join(Cliente, VentaEncabezado.IdCliente == Cliente.Id).join(VentaDetalle, VentaEncabezado.Id == VentaDetalle.IdVentaEncabezado).join(Producto, VentaDetalle.IdProducto == Producto.Id).filter(VentaEncabezado.FProxCuota == selected_date).all()
    cuotas = (db.session.query(VentaEncabezado, Cliente, Producto.Nombre)
            .join(Cliente, VentaEncabezado.IdCliente == Cliente.Id)
            .join(VentaDetalle, VentaEncabezado.Id == VentaDetalle.IdVentaEncabezado)
            .join(Producto, VentaDetalle.IdProducto == Producto.Id)
            .filter(VentaEncabezado.FProxCuota == selected_date, VentaEncabezado.PreCerrado == 0)
            .all())
    
    # Agrupar las cuotas por nombre de producto
    cuotas_por_producto = defaultdict(list)
    for venta, cliente, producto_nombre in cuotas:
        cuotas_por_producto[producto_nombre].append((venta, cliente))
    
    num_cuotas = len(cuotas)

    if request.method == 'POST' and 'update_id' in request.form:
        cuota_id = request.form.get('update_id')
        new_date_str = request.form.get(f'new_date_{cuota_id}')
        if new_date_str:
            new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
            # Validar que la nueva fecha no sea más de 15 días desde hoy
            if new_date <= max_date:
                cuota = VentaEncabezado.query.get(cuota_id)
                cuota.FProxCuota = new_date
                cuota.Pospuesta = (cuota.Pospuesta or 0) + 1
                cuota.FUpdPospuesta = datetime.now()
                db.session.commit()
                return redirect(url_for('cuotas_dia', usuario=usuario, selected_date=selected_date))
            else:
                flash("La nueva fecha no puede ser más de 15 días desde hoy.", "error")

    return render_template('cuotas_dia.html', permisos=permisos, usuario=usuario, cuotas_por_producto=cuotas_por_producto, num_cuotas=num_cuotas, selected_date=selected_date, today=today, max_date=max_date)




@app.route('/menu/gastos/crear/<usuario>', methods=['GET', 'POST'])
def crear_gastos(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."

    permisosCrear = usuarios.get(usuario, {}).get('permisos', {}).get('cobros', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})

    if request.method == 'POST':
        # Recogiendo los datos del formulario
        FechaGasto = request.form['FechaGasto']
        NumFactura = request.form['NumFactura']
        Descripcion = request.form['Descripcion']
        Importe = request.form['Importe']

        # Tratamiento de la imagen
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            nombre_archivo = secure_filename(imagen.filename)
            ruta_guardado = os.path.join('/home/soporte/Imagenes_Gastos', nombre_archivo)
            imagen.save(ruta_guardado)

            # Crear el registro de gasto en la base de datos
            try:
                gasto = Gasto(FechaGasto=FechaGasto, NumFactura=NumFactura, Descripcion=Descripcion, Importe=Importe, Ruta=ruta_guardado)
                db.session.add(gasto)
                db.session.commit()
                return "¡CORRECTO! TODO HA IDO BIEN."
            except Exception as e:
                # Aquí podrías registrar el error 'e' en algún log para futuras revisiones
                return f"Ups... Ha ocurrido el siguiente error: {e}"

    if 'crear' in permisosCrear:
        return render_template('crear_gastos.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."


    
@app.route('/menu/gastos/consultar/<usuario>', methods=['GET', 'POST'])
@login_required
def consultar_gastos(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('gastos', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    
    if 'consultar' not in permisosConsultar:
        return "No tienes permisos para ver esta página."

    gastos = []  # Lista vacía para inicializar los gastos

    if request.method == 'POST':
        FechaGastoDesde = request.form.get('FechaGastoDesde')
        FechaGastoHasta = request.form.get('FechaGastoHasta')
        NumFactura = request.form.get('NumFactura')
        Importe = request.form.get('Importe')
        usuarios_seleccionados = request.form.getlist('NombreUsuario[]')  # Lista de IDs de usuarios seleccionados

        # Iniciamos la consulta
        query = db.session.query(Gasto)

        # Filtramos la consulta según los datos recibidos
        if FechaGastoDesde:
            query = query.filter(Gasto.FechaGasto >= FechaGastoDesde)
        if FechaGastoHasta:
            query = query.filter(Gasto.FechaGasto <= FechaGastoHasta)
        if NumFactura:
            query = query.filter(Gasto.NumFactura == NumFactura)
        if Importe:
            query = query.filter(Gasto.Importe == float(Importe))
        if usuarios_seleccionados:
            query = query.filter(Gasto.IdUsuario.in_(usuarios_seleccionados))

        gastos = query.all()

    return render_template('consultar_gastos.html', permisos=permisos, usuario=usuario, gastos=gastos)


@app.route('/menu/inicio/<usuario>')
@login_required
def inicio_web(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('gastos', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    
    if 'consultar' in permisosConsultar:

            return render_template('inicio.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."


@app.route('/menu/admin/crear/<usuario>', methods=['GET', 'POST'])
@login_required
def cierre_mes(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."

    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if request.method == 'POST':
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']

        # Llama al procedimiento almacenado con parámetros ficticios
        resultados = Info_para_Dashboar(fecha_inicio, fecha_fin, 'NO')
        
        # Define las columnas que deberían ser formateadas como moneda
        columnas_monetarias = ['$ Capital', '$ Venta','$ Pagos','$ Pendiente','$ Abonos','$ Inicial']  # Reemplaza con los nombres reales de las columnas
        # Define los títulos específicos para cada conjunto de resultados
        titulos = [
            "Estado de la cartera",
            "Venta/Cobro por mes y producto",
            "Cobro por mes, producto y responsable"
        ]

        if len(resultados) >= 3:
            # Pasar los resultados a la plantilla
            return render_template('cierre_mes.html', permisos=permisos, usuario=usuario, resultados=resultados, columnas_monetarias=columnas_monetarias, titulos=titulos)
    # Si no hay resultados o el método no es POST, renderizar la página sin resultados
    return render_template('cierre_mes.html', permisos=permisos, usuario=usuario, resultados=[], columnas_monetarias=[], titulos=[])




@app.route('/menu/admin/consultar/<usuario>', methods=['GET', 'POST'])
@login_required
def dashboard(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."

    permisos = usuarios.get(usuario, {}).get('permisos', {})

    # Llama al procedimiento almacenado con parámetros ficticios
    resultados = Info_para_Dashboar('', '', 'SI')
    
    # Define las columnas que deberían ser formateadas como moneda
    columnas_monetarias = ['$ Capital', '$ Venta','$ Pagos','$ Pendiente','$ Abonos','$ Inicial']  # Reemplaza con los nombres reales de las columnas
    # Define los títulos específicos para cada conjunto de resultados
    titulos = [
        "Estado de la cartera",
        "Indicador de",
        "Cobro por mes, producto y responsable"
    ]

    if len(resultados) >= 3:
        # Pasar los resultados a la plantilla
        print(json.dumps(resultados[2], indent=2))
        return render_template('dashboard.html', permisos=permisos, usuario=usuario, resultados=resultados[1], columnas_monetarias=columnas_monetarias, titulo=titulos[1])
    
    # Si no hay resultados, renderizar la página sin resultados
    return render_template('dashboard.html', permisos=permisos, usuario=usuario, resultados=[], columnas_monetarias=[], titulo="")



def Info_para_Dashboar(param1, param2, param3):
    try:
        # Establecer la conexión y el cursor
        conn = db.session.connection().connection
        cursor = conn.cursor()
        
        # Llamar al procedimiento almacenado
        cursor.callproc('LiquidacionMes', [param1, param2, param3])

        todos_resultados = []

        # Iterar sobre cada conjunto de resultados
        while True:
            if cursor.description:
                columnas = [desc[0] for desc in cursor.description]
                # Omitir el conjunto de resultados de estadísticas
                if 'Updated Rows' in columnas and 'Start time' in columnas and 'Finish time' in columnas:
                    if not cursor.nextset():
                        break
                    continue
                
                filas = cursor.fetchall()
                resultado = [dict(zip(columnas, fila)) for fila in filas]
                todos_resultados.append(resultado)
            
            # Avanzar al siguiente conjunto de resultados
            if not cursor.nextset():
                break

        # Cerrar el cursor
        cursor.close()

        return todos_resultados

    except Exception as e:
        # Manejo de errores
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return None




@app.route('/menu/buscador/<usuario>', methods=['GET', 'POST'])
@login_required
def buscador(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."

    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('clientes', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    
    if 'consultar' in permisosConsultar:
        if request.method == 'POST':
            termino_busqueda = request.form['termino_busqueda']
            campo_busqueda = request.form['campo_busqueda']

            # Realizamos la búsqueda de datos
            resultados = buscar_datos(termino_busqueda, campo_busqueda)
            # Renderizamos la plantilla con los resultados de la búsqueda
            return render_template('buscador.html', permisos=permisos, usuario=usuario, resultados=resultados)
        else:
            return render_template('buscador.html', permisos=permisos, usuario=usuario)
            
    else:
        return "No tienes permisos para ver esta página."

@app.route('/get_usuarios', methods=['GET'])
def get_usuarios():
    # Término de búsqueda
    search_term = request.args.get('q')

    # Si hay un término de búsqueda, filtramos por ese término
    if search_term:
        usuarios = Usuario.query.filter(Usuario.Nombre.like(f"%{search_term}%")).all()
    else:
        usuarios = Usuario.query.all()

    # Convertir la lista de usuarios a formato JSON
    lista_usuarios = [{'id': str(u.Id), 'text': u.Nombre} for u in usuarios]
    
    return jsonify(results=lista_usuarios)

@app.route('/get_clientes', methods=['GET'])
def buscar_clientes():
    search_term = request.args.get('q')  # Usamos 'q' para coincidir con la configuración de Select2
    if search_term:
        # Realizamos una búsqueda en la columna 'Nombres' en la tabla 'Clientes'
        clientes = Cliente.query.filter(Cliente.Nombres.like(f"%{search_term}%")).all()
    else:
        # Si no hay término de búsqueda, podemos devolver una lista vacía o los primeros N clientes
        clientes = []

    # Convertimos los resultados en el formato necesario para Select2
    resultados = [{'id': cliente.Id, 'text': f"{cliente.Nombres} {cliente.Apellidos}"} for cliente in clientes]

    # Añadimos una opción para crear un nuevo cliente en caso de que no se encuentre en la lista
    resultados.append({'id': 'nuevo', 'text': 'Crear nuevo cliente'})

    return jsonify(results=resultados)

@app.route('/get_productos', methods=['GET'])
def get_productos():
    search = request.args.get('q', '')  # Obtener el término de búsqueda
    productos_query = Producto.query.filter(Producto.Nombre.ilike(f"%{search}%")).all()  # Filtrar productos por nombre

    productos = []
    for producto in productos_query:
        productos.append({
            "id": producto.Id,  # Asegúrate de que tu modelo de Producto tenga un atributo 'Id'
            "text": producto.Nombre  # Asumo que tu modelo de Producto tiene un atributo 'Nombre'
        })

    return jsonify({"results": productos})

@app.route('/get_tipos_compromiso', methods=['GET'])
def get_tipos_compromiso():
    search = request.args.get('q', '')  # Obtener el término de búsqueda
    tipos_query = CompromisoDePago.query.filter(Producto.Nombre.ilike(f"%{search}%")).all()   # Asumo que tienes un modelo llamado TipoCompromiso

    tipos = []
    for tipo in tipos_query:
        tipos.append({
            "id": tipo.Id,
            "text": tipo.Nombre  # Asumo que tu modelo tiene un atributo 'nombre'
        })

    return jsonify({"results": tipos})

@app.route('/get_calculo/<int:IdVentaEncabezado>', methods=['GET'])
def get_calculo(IdVentaEncabezado):
    try:
        venta_encabezado = VentaEncabezado.query.get(IdVentaEncabezado)
        if not venta_encabezado:
            return jsonify({'message': 'Venta Encabezado no encontrada'}), 404

        importe_venta = venta_encabezado.ImporteVenta
        importe_inicial = venta_encabezado.ImporteInicial

        cuotas = Cuota.query.filter_by(IdVentaEncabezado=IdVentaEncabezado).all()
        suma_abonos = sum(cuota.Abono for cuota in cuotas)

        calculo = importe_venta - importe_inicial - suma_abonos

        return jsonify({'calculo': calculo}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


from sqlalchemy.exc import SQLAlchemyError

@app.route('/get_tarjeta/<numero_tarjeta>', methods=['GET'])
def get_tarjeta(numero_tarjeta):
    try:
        encabezado = VentaEncabezado.query.filter_by(NumTarjeta=numero_tarjeta).first()
        if encabezado:
            cuotas = Cuota.query.filter_by(IdVentaEncabezado=encabezado.Id).all()
            cuotas_dict = [c.to_dict() for c in cuotas]  # Asumiendo que tienes un método to_dict en el modelo
            # Convertir cualquier dato de tipo bytes a str
            encabezado_dict = encabezado.to_dict()
            for key, value in encabezado_dict.items():
                if isinstance(value, bytes):
                    encabezado_dict[key] = value.decode('utf-8')  # Convertir bytes a str
            return jsonify({'encabezado': encabezado_dict, 'cuotas': cuotas_dict}), 200
        else:
            return jsonify({'message': 'Tarjeta no encontrada'}), 404
    except SQLAlchemyError as e:
        app.logger.error(f"Error al acceder a la base de datos: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500
    except Exception as e:
        app.logger.error(f"Error desconocido: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500

@app.route('/get_medios_pago', methods=['GET'])
def get_medios_pago():
    try:
        medios = MedioDePago.query.all()
        medios_dict = [m.to_dict() for m in medios]
        return jsonify({'medios': medios_dict}), 200
    except Exception as e:
        app.logger.error(f"Error desconocido: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500


@app.route('/sumar_abonos/<int:id_venta_encabezado>', methods=['GET'])
def sumar_abonos(id_venta_encabezado):
    try:
        total_abonos = db.session.query(db.func.sum(Cuota.Abono)).filter(Cuota.IdVentaEncabezado == id_venta_encabezado).scalar()
        total_abonos = total_abonos if total_abonos else 0  # En caso de que no haya abonos, el total será 0
        return jsonify({'total_abonos': total_abonos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_prod_tarjeta/<numero_tarjeta>', methods=['GET'])
def get_prod_tarjeta(numero_tarjeta):
    try:
        # Ejecutar el procedimiento almacenado getTarjetaEncabezado
        cursor_encabezado = db.session.connection().connection.cursor()
        cursor_encabezado.callproc('getTarjetaEncabezado', [numero_tarjeta])
        resultados_encabezado = [dict(zip([column[0] for column in cursor_encabezado.description], row)) for row in cursor_encabezado.fetchall()]
        cursor_encabezado.close()

        # Ejecutar el procedimiento almacenado getTarjetaProductos
        cursor_productos = db.session.connection().connection.cursor()
        cursor_productos.callproc('getTarjetaProductos', [numero_tarjeta])
        resultados_productos = [dict(zip([column[0] for column in cursor_productos.description], row)) for row in cursor_productos.fetchall()]
        cursor_productos.close()

        # Confirmar los cambios (en caso de que los procedimientos hayan modificado la base de datos)
        db.session.commit()

        return jsonify({
            'encabezado': resultados_encabezado,
            'productos': resultados_productos,
        }), 200
    except db.SQLAlchemyError as e:
        app.logger.error(f"Error al acceder a la base de datos: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500
    except Exception as e:
        app.logger.error(f"Error desconocido: {str(e)}")
        return jsonify({'message': 'Error en el servidor'}), 500
    
@app.route('/verificar_tarjeta/<numero_tarjeta>', methods=['GET'])
def verificar_tarjeta(numero_tarjeta):
    try:
        # Realiza la lógica de verificación de la tarjeta en la base de datos.
        venta_encabezado = VentaEncabezado.query.filter_by(NumTarjeta=numero_tarjeta).first()

        if venta_encabezado:
            resultado = {"ID": 1, "Mensaje": "La tarjeta existe en la BBDD"}
        else:
            resultado = {"ID": 0, "Mensaje": "La tarjeta no existe en la BBDD)"}

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"ID": 0, "Mensaje": str(e)}), 500  # Devuelve un mensaje de error en formato JSON

@app.route('/descargar_informe_cobros', methods=['POST'])
def descargar_informe_cobros():
    resultados_informe = session.get('resultados_informe')
    if resultados_informe:
        # Generar el archivo Excel y devolverlo como una descarga
        df_resultados = pd.DataFrame(resultados_informe)
        output = io.BytesIO()
        df_resultados.to_excel(output, index=False, sheet_name='Sheet1')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='Informe_Cobros.xlsx')
    else:
        return "No hay resultados para descargar."

def byte_to_bool(byte_value):
    return byte_value == b'\x01'

def buscar_datos(termino_busqueda, campo_busqueda):
    if campo_busqueda == 'nombre':
        clientes = Cliente.query.filter(Cliente.Nombres.like(f'%{termino_busqueda}%')).all()
    elif campo_busqueda == 'dni':
        clientes = Cliente.query.filter(Cliente.DNI.like(f'%{termino_busqueda}%')).all()
    elif campo_busqueda == 'apellido':
        clientes = Cliente.query.filter(Cliente.Apellidos.like(f'%{termino_busqueda}%')).all()
    elif campo_busqueda == 'telefono':
        clientes = Cliente.query.filter(or_(
            Cliente.Telefono1.like(f'%{termino_busqueda}%')),
            Cliente.Telefono2.like(f'%{termino_busqueda}%'),
            Cliente.Telefono3.like(f'%{termino_busqueda}%')
        ).all()
    elif campo_busqueda == 'direccion':
        clientes = Cliente.query.filter(Cliente.Direccion.like(f'%{termino_busqueda}%')).all()
    else:
        clientes = []

    if not clientes:
        return []

    resultados = []

    for cliente in clientes:
        query = text("""
            SELECT
                Id, IdCliente, ImporteVenta, ImporteInicial, ImporteAbonos, SaldoPendiente, NumCuotas,
                ImporteCuota, FVenta, FProxCuota, NumTarjeta, IdCompPago, IdUsuario, PreCerrado,
                Cerrado, Ciudad, Responsable, Comentario, Auditado, Cancelada, Anulada, Perdida,
                VLiquidada, FCreado, Pospuesta, FUpdPospuesta
            FROM
                VentasEncabezados
            WHERE
                IdCliente = :id_cliente
        """)

        ventas_cliente = db.session.execute(query, {'id_cliente': cliente.Id}).fetchall()

        for venta in ventas_cliente:
            abonos = db.session.query(func.sum(Cuota.Abono)).filter_by(IdVentaEncabezado=venta.Id).scalar()
            if abonos is None:
                abonos = 0
            importe_pendiente = venta.ImporteVenta - (venta.ImporteInicial + abonos)

            # Convertir valores booleanos desde bytes a booleanos
            cerrado = byte_to_bool(venta.Cerrado)
            precerrado = byte_to_bool(venta.PreCerrado)
            auditado = byte_to_bool(venta.Auditado)
            cancelada = byte_to_bool(venta.Cancelada)
            anulada = byte_to_bool(venta.Anulada)
            perdida = byte_to_bool(venta.Perdida)
            vliquidada = byte_to_bool(venta.VLiquidada)

            print(f"Venta ID: {venta.Id}, Cerrado: {cerrado}, PreCerrado: {precerrado}, Auditado: {auditado}")

            resultados.append({
                'num_tarjeta': venta.NumTarjeta,
                'nombre': cliente.Nombres,
                'apellido': cliente.Apellidos,
                'telefono': cliente.Telefono1,
                'direccion': cliente.Direccion,
                'dni': cliente.DNI,
                'importe_venta': venta.ImporteVenta,
                'importe_pend': importe_pendiente,
                'num_cuotas': venta.NumCuotas,
                'f_prox_cuota': venta.FProxCuota,
                'cerrado': cerrado,
                'precerrado': precerrado,
                'auditado': auditado,
                'cancelada': cancelada,
                'anulada': anulada,
                'perdida': perdida,
                'vliquidada': vliquidada
            })
    
    if not resultados:
        print("No se encontraron resultados.")
    
    print("Resultados encontrados:", resultados)
    return resultados



@app.route('/visualizar_archivo/<filename>')
def visualizar_archivo(filename):
    return send_from_directory('/home/soporte/Imagenes_Gastos', filename, as_attachment=False)

@app.route('/descargar_archivo/<filename>')
def descargar_archivo(filename):
    return send_from_directory('/home/soporte/Imagenes_gastos', filename, as_attachment=True, download_name=filename)


if __name__ == '__main__':
   app.run(debug=True, port=8000)

# if __name__ == '__main__':
#     app.run()
