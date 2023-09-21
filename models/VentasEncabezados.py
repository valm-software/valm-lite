from database import db

class VentaEncabezado(db.Model):
    __tablename__ = 'VentasEncabezados'
    Id = db.Column(db.Integer, primary_key=True)
    IdCliente = db.Column(db.Integer, db.ForeignKey('Clientes.Id'))
    ImporteVenta = db.Column(db.Numeric(10, 2))
    ImporteInicial = db.Column(db.Numeric(10, 2))
    NumCuotas = db.Column(db.Integer)
    ImporteCuota = db.Column(db.Numeric(10, 2), server_default="0")
    FVenta = db.Column(db.DateTime)
    FProxCuota = db.Column(db.Date)
    NumTarjeta = db.Column(db.Integer)
    IdCompPago = db.Column(db.Integer, db.ForeignKey('CompromisoDePagos.Id'))
    IdUsuario = db.Column(db.Integer, db.ForeignKey('Usuarios.Id'))
    Cerrado = db.Column(db.Boolean, default=False)

    # # Definir las relaciones con otras tablas
    # cliente = db.relationship('Cliente', backref='ventas', lazy=False)
    # compromiso = db.relationship('CompromisoDePago', backref='ventas', lazy=True)
