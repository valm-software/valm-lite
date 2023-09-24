from database import db

class Gasto(db.Model):
    __tablename__ = 'Gastos'
    Id = db.Column(db.Integer, primary_key=True)
    FechaGasto = db.Column(db.Date)
    NumFactura = db.Column(db.String(100))
    Descripcion = db.Column(db.String(250))
    Importe = db.Column(db.Numeric(10, 2))
    IdUsuario = db.Column(db.Integer, db.ForeignKey('Usuarios.Id'))
    Ruta = db.Column(db.String(250))
    Creado = db.Column(db.DateTime)

    # # Definir la relación uno a muchos con VentasEncabezados
    # ventas_encabezados = db.relationship('VentaEncabezado', backref='cliente', lazy=True)
