from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify,send_from_directory
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

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

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
            'cobros': ['crear', 'consultar'],
            'gastos': ['crear', 'consultar'],
            'inicio': ['crear', 'consultar']
        }
    },
    'adrian.ad': {
        'password': 'adrian.ad',
        'permisos': {
            'tarjetas': ['crear', 'consultar'],
            'clientes': ['crear', 'consultar'],
            'cobros': ['crear', 'consultar']
        }
    },    
    'fray.lm': {
        'password': 'fray.lm',
        'permisos': {
            'tarjetas': ['crear', 'consultar'],
            'clientes': ['crear'],
            'cobros': ['crear', 'consultar']
        }
    },
    'parra.pa': {
        'password': 'parra.pa',
        'permisos': {
            'tarjetas': [],
            'clientes': ['consultar'],
            'cobros': ['crear', 'consultar']
        }
    },
  
    'auxiliar.au': {
        'password': 'auxiliar123',
        'permisos': {}
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


@app.route('/menu/cobros/consultar/<usuario>')
@login_required
def consultar_cobro(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('tarjetas', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'consultar' in permisosConsultar:
        return render_template('consultar_cobro.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."

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
            ruta_guardado = os.path.join('Imagenes_gastos', nombre_archivo)
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


@app.route('/get_tarjeta/<numero_tarjeta>', methods=['GET'])
def get_tarjeta(numero_tarjeta):
    try:
        encabezado = VentaEncabezado.query.filter_by(NumTarjeta=numero_tarjeta).first()
        if encabezado:
            cuotas = Cuota.query.filter_by(IdVentaEncabezado=encabezado.Id).all()
            cuotas_dict = [c.to_dict() for c in cuotas]  # Asumiendo que tienes un método to_dict en el modelo
            return jsonify({'encabezado': encabezado.to_dict(), 'cuotas': cuotas_dict}), 200
        else:
            return jsonify({'message': 'Tarjeta no encontrada'}), 404
    except db.SQLAlchemyError as e:
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

@app.route('/visualizar_archivo/<filename>')
def visualizar_archivo(filename):
    return send_from_directory('Imagenes_gastos', filename, as_attachment=False)

@app.route('/descargar_archivo/<filename>')
def descargar_archivo(filename):
    return send_from_directory('Imagenes_gastos', filename, as_attachment=True, download_name=filename)


if __name__ == '__main__':
   app.run(debug=True, port=8000)

# if __name__ == '__main__':
#     app.run()
