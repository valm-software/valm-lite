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
    TelPreInter = db.Column(db.String(3))
    TelArea = db.Column(db.String(4))
    TelL1 = db.Column(db.String(4))
    TelL2 = db.Column(db.String(4))
    TelMovil = db.Column(db.Boolean)
    TelValido = db.Column(db.Boolean)
    TelAuditado = db.Column(db.Boolean)   
    Telefono1Back = db.Column(db.String(100))   

    # # Definir la relación uno a muchos con VentasEncabezados
    # ventas_encabezados = db.relationship('VentaEncabezado', backref='cliente', lazy=True)
