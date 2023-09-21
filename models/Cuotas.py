from database import db

class Cuota(db.Model):
    __tablename__ = 'Cuotas'
    Id = db.Column(db.Integer, primary_key=True)
    IdVentaEncabezado = db.Column(db.Integer, db.ForeignKey('VentasEncabezados.Id'))
    IdMedioDePago = db.Column(db.Integer, db.ForeignKey('MediosDePagos.Id'))
    IdUsuario = db.Column(db.Integer, db.ForeignKey('Usuarios.Id'))
    FechaPago = db.Column(db.DateTime)
    NumCuota = db.Column(db.Integer)
    Abono = db.Column(db.Numeric(10, 2))
    Saldo = db.Column(db.Numeric(10, 2))
    Liquidado = db.Column(db.Boolean)
    FechaLiquidacion = db.Column(db.DateTime)

    # Definir las relaciones con otras tablas
    venta_encabezado = db.relationship('VentaEncabezado', backref='cuotas', lazy=True)
    medio_de_pago = db.relationship('MedioDePago', backref='cuotas', lazy=True)
    usuario = db.relationship('Usuario', backref='cuotas', lazy=True)
