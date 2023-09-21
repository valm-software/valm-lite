from database import db

class CompromisoDePago(db.Model):
    __tablename__ = 'CompromisoDePagos'
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(255))
    Descripcion = db.Column(db.String(50))

    # Definir la relación uno a muchos con VentasEncabezados
    ventas_encabezados = db.relationship('VentaEncabezado', backref='compromiso', lazy=True)
