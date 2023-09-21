from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import mysql.connector
from flask_session import Session
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configurar la sesión para que caduque después de 2 horas de inactividad
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

Session(app)

# Datos de ejemplo: usuarios y permisos
usuarios = {
    'victor.lm': {
        'password': 'victor.lm',
        'permisos': {
            'tarjetas': ['crear', 'consultar'],
            'clientes': ['crear', 'consultar'],
            'cobros': ['crear', 'consultar']
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



def conectar_db():
    try:
        connection = mysql.connector.connect(
            host="192.168.1.199",
            user="javier",
            password="valm2023",
            database="bd_valm_lite"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Función para ejecutar las consultas (la misma que antes)
def ejecutar_consultas(connection, id_venta):
    # Consultas SQL proporcionadas
    queries = [
        f"""
       select a.id as 'Nº Fac',
       a.NumTarjeta as 'Nº Tarjeta', 
       substring(a.FVenta,1,10) as 'F. Venta',
       b.DNI as 'DNI',
       b.Nombres as 'Nombre',
       b.Apellidos as 'Apellido',
       b.Telefono1 as 'Teléfono',
       b.Direccion as 'Dirección',
       concat(FORMAT(a.ImporteVenta, 2, 'es_ES'),'$') as 'Importe Venta',
       concat(FORMAT(a.ImporteInicial, 2, 'es_ES'),'$') as 'Importe Inicial',
       a.NumCuotas as 'Nª Cuotas',
       IFNULL(e.NumcuotasPagadas, 0) AS 'Nº Cuotas Pagadas',
       IFNULL(concat(FORMAT(e.ImpCuotaspagadas, 2, 'es_ES'),'$'), 0) AS 'Imp Cuotas Pagadas',       
       concat(FORMAT(ImporteVenta - (ImporteInicial + IFNULL(e.ImpCuotaspagadas, 0)), 2, 'es_ES'),'$') as 'Imp Pendiente',
       concat(FORMAT(a.ImporteCuota, 2, 'es_ES'),'$') as 'Imp Cuota',
       a.FProxCuota as 'F. Proxima Cuota',
       c.Nombre as 'Periosidad de cobro',
       d.Nombre as 'Vendedor',
		  CASE a.Cerrado 
		      WHEN 1 THEN 'SI'
		      ELSE 'NO'
		  END AS 'Cerrado'		   
        from VentasEncabezados as a 
        inner join Clientes as b on a.IdCliente  = b.Id 
        inner join CompromisoDePagos as c on a.IdCompPago  = c.Id 
        inner join Usuarios as d on a.IdUsuario = d.Id 
        LEFT JOIN (
            SELECT
                IdVentaEncabezado,
                SUM(Abono) AS ImpCuotaspagadas,
                count(id) AS NumcuotasPagadas
            FROM Cuotas
            GROUP BY IdVentaEncabezado
        ) AS e ON a.id = e.IdVentaEncabezado
        where a.NumTarjeta ={id_venta};
        """,
        
        f"""
        select b.Id as IdProducto,
	    b.Nombre,
	     b.Descripcion,
	    a.cantidad as 'Cantidad'
        from VentasDetalles as a 
        inner join Productos  as b on a.IdProducto  = b.Id
        inner join VentasEncabezados as c on a.IdVentaEncabezado = c.Id 
        where c.NumTarjeta = {id_venta};
        """,
        
        f"""
        select  c.nombre as Cobrador ,
        a.NumCuota as 'Nº Cuota',
        SUBSTR(a.fechaPago,1,10) as 'F. Pago',
        concat(FORMAT(a.abono, 2, 'es_ES'),'$') AS Abono,
        concat(FORMAT(a.saldo, 2, 'es_ES'),'$') as Saldo,
		  CASE a.liquidado
		      WHEN 1 THEN 'SI'
		      ELSE 'NO'
		  END as 'Liquidado',        
        substring(fechaLiquidacion,1,10)as 'F. Liquidado'        
        from Cuotas as a
        inner join MediosDePagos as b on a.IdMedioDePago  = b.Id
        inner join Usuarios as c on a.IdUsuario = c.Id 
        inner join VentasEncabezados as d on a.IdVentaEncabezado  = d.Id 
        where d.NumTarjeta  = {id_venta};
        """
    ]
    
    results = []
    cursor = connection.cursor(dictionary=True)  
    for query in queries:
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
            results.append(result)
    cursor.close()
    return results




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
            return redirect(url_for('menu', usuario=usuario))
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

@app.route('/menu/tarjetas/consultar/<usuario>')
@login_required
def consultar_tarjeta(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('tarjetas', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'consultar' in permisosConsultar:
        return render_template('consultar_tarjeta.html', permisos=permisos, usuario=usuario)
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



@app.route('/menu/clientes/consultar/<usuario>')
@login_required
def consultar_cliente(usuario):
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('clientes', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    if 'consultar' in permisosConsultar:
        return render_template('consultar_cliente.html', permisos=permisos, usuario=usuario)
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

@app.route('/menu/cobros/consultar/<usuario>', methods=['GET', 'POST'])
@login_required
def consultar_cobro(usuario):
    connection = None  # <-- Inicialización de la variable connection
    resultados = None
    if usuario != session['usuario']:
        return "Acceso denegado: No puedes acceder a esta página."
    permisosConsultar = usuarios.get(usuario, {}).get('permisos', {}).get('cobros', [])
    permisos = usuarios.get(usuario, {}).get('permisos', {})
    
    if request.method == 'POST':
        id_venta = request.form['id_venta']
        connection = conectar_db()

    if connection:
        resultados = ejecutar_consultas(connection, id_venta)
        connection.close()
    if 'consultar' in permisosConsultar:
        return render_template('consultar_cobro.html', permisos=permisos, usuario=usuario, resultados=resultados)
    else:
        return "No tienes permisos para ver esta página."





if __name__ == '__main__':
   app.run(debug=True, port=8000)
