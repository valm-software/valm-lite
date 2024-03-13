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
    Cerrado = db.Column(db.String(1))
    Ciudad = db.Column(db.String(255))
    Responsable = db.Column(db.String(255))
    Comentario = db.Column(db.String(256))
    Auditado = db.Column(db.Boolean)
    Cancelada = db.Column(db.Boolean)
    Anulada = db.Column(db.Boolean)
    Perdida = db.Column(db.Boolean)
    VLiquidada = db.Column(db.Boolean)
    FCreado = db.Column(db.DateTime)
   


    # # Definir las relaciones con otras tablas
    # cliente = db.relationship('Cliente', backref='ventas', lazy=False)
    # compromiso = db.relationship('CompromisoDePago', backref='ventas', lazy=True)
    cuotas = db.relationship('Cuota', backref='venta_encabezado', lazy=True)
    def to_dict(self):
        return {
            'Id': self.Id,
            'IdCliente': self.IdCliente,
            'ImporteVenta': self.ImporteVenta,
            'ImporteInicial': self.ImporteInicial,
            'NumCuotas': self.NumCuotas,
            'ImporteCuota': self.ImporteCuota,
            'FVenta': self.FVenta,
            'FProxCuota': self.FProxCuota,
            'NumTarjeta': self.NumTarjeta,
            'IdCompPago': self.IdCompPago,
            'IdUsuario': self.IdUsuario,
            'Cerrado': self.Cerrado,
            'Ciudad': self.Ciudad,
            'Responsable': self.Responsable,
            'Comentario': self.Comentario
        }