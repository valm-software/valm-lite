from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
import mysql.connector
from flask_session import Session
from datetime import timedelta
from functools import wraps
from database import init_app
from models.Clientes import db, Cliente
from models.VentasEncabezados import db, VentaEncabezado

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configurar la sesión para que caduque después de 2 horas de inactividad
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

Session(app)


# Configura la conexión a la base de datos desde database.py
init_app(app)


# Datos de ejemplo: usuarios y permisos
usuarios = {
    'victor.lm': {
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
@app.route('/menu/tarjetas/crear/<usuario>')
@login_required
def crear_tarjeta(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosCrear = usuarios.get(usuario, {}).get('permisos', {}).get('tarjetas', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'crear' in permisosCrear:
        return render_template('crear_tarjeta.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."




from flask import request, render_template

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
            # print('resultados_encabezado: ', resultados_encabezado)            
            
            # Ejecutar el procedimiento almacenado getTarjetaProductos
            cursor_productos = db.session.connection().connection.cursor()
            cursor_productos.callproc('getTarjetaProductos', [id_venta])
            resultados_productos = [dict(zip([column[0] for column in cursor_productos.description], row)) for row in cursor_productos.fetchall()]
            cursor_productos.close()
            # print('resultados_productos: ', resultados_productos)
            
            # Ejecutar el procedimiento almacenado getTarjetaCuotas
            cursor_cuotas = db.session.connection().connection.cursor()
            cursor_cuotas.callproc('getTarjetaCuotas', [id_venta])
            resultados_cuotas = [dict(zip([column[0] for column in cursor_cuotas.description], row)) for row in cursor_cuotas.fetchall()]
            cursor_cuotas.close()
            # print('resultados_cuotas: ', resultados_cuotas)

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




@app.route('/menu/cobros/crear/<usuario>')
@login_required
def crear_cobro(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosCrear = usuarios.get(usuario, {}).get('permisos', {}).get('cobros', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'crear' in permisosCrear:
        return render_template('crear_cobro.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."

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

@app.route('/menu/gastos/crear/<usuario>')
@login_required
def crear_gastos(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosCrear = usuarios.get(usuario, {}).get('permisos', {}).get('gastos', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'crear' in permisosCrear:
        return render_template('crear_gastos.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."

@app.route('/menu/gastos/consultar/<usuario>')
@login_required
def consultar_gastos(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('gastos', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'consultar' in permisosConsultar:
        return render_template('consultar_gastos.html', permisos=permisos, usuario=usuario)
    else:
        return "No tienes permisos para ver esta página."


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

if __name__ == '__main__':
   app.run(debug=True, port=8000)

