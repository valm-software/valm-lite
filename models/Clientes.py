from database import db

class Cliente(db.Model):
    __tablename__ = 'Clientes'
    Id = db.Column(db.Integer, primary_key=True)
    DNI = db.Column(db.String(50))
    Nombres = db.Column(db.String(255))
    Apellidos = db.Column(db.String(255))
    Telefono1 = db.Column(db.String(50))
    Telefono2 = db.Column(db.String(50))
    Telefono3 = db.Column(db.String(50))
    Direccion = db.Column(db.String(255))
    Ubicacion = db.Column(db.String(255))
    Nota = db.Column(db.String(255))

    # # Definir la relación uno a muchos con VentasEncabezados
    # ventas_encabezados = db.relationship('VentaEncabezado', backref='cliente', lazy=True)
