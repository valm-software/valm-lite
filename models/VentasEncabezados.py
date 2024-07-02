from datetime import datetime

from sqlalchemy import func
from database import db

class VentaEncabezado(db.Model):
    __tablename__ = 'VentasEncabezados'
    Id = db.Column(db.Integer, primary_key=True)
    IdCliente = db.Column(db.Integer, db.ForeignKey('Clientes.Id'))
    ImporteVenta = db.Column(db.Numeric(10, 2))
    ImporteInicial = db.Column(db.Numeric(10, 2))
    ImporteAbonos = db.Column(db.Numeric(10, 2))
    SaldoPendiente = db.Column(db.Numeric(10, 2))
    NumCuotas = db.Column(db.Integer)
    ImporteCuota = db.Column(db.Numeric(10, 2), server_default="0")
    FVenta = db.Column(db.DateTime)
    FProxCuota = db.Column(db.Date)
    NumTarjeta = db.Column(db.Integer)
    IdCompPago = db.Column(db.Integer, db.ForeignKey('CompromisoDePagos.Id'))
    IdUsuario = db.Column(db.Integer, db.ForeignKey('Usuarios.Id'))
    PreCerrado = db.Column(db.Boolean, default=False)  # Usar db.Boolean y default=False
    Cerrado = db.Column(db.Boolean, default=False)  # Usar db.Boolean y default=False
    Ciudad = db.Column(db.String(255))
    Responsable = db.Column(db.String(255))
    Comentario = db.Column(db.String(256))
    Auditado = db.Column(db.Boolean, default=False)
    Cancelada = db.Column(db.Boolean, default=False)
    Anulada = db.Column(db.Boolean, default=False)
    Perdida = db.Column(db.Boolean, default=False)
    VLiquidada = db.Column(db.Boolean, default=False)
    FCreado = db.Column(db.DateTime, default=func.now())  # Utiliza func.now() para la fecha y hora actuales
    Pospuesta = db.Column(db.Integer, default=0)
    FUpdPospuesta = db.Column(db.DateTime)
      


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
            'ImporteAbonos' : self.ImporteAbonos,
            'SaldoPendiente': self.SaldoPendiente,
            'NumCuotas': self.NumCuotas,
            'ImporteCuota': self.ImporteCuota,
            'FVenta': self.FVenta,
            'FProxCuota': self.FProxCuota,
            'NumTarjeta': self.NumTarjeta,
            'IdCompPago': self.IdCompPago,
            'IdUsuario': self.IdUsuario,
            'PreCerrado': self.PreCerrado,
            'Cerrado': self.Cerrado,
            'Ciudad': self.Ciudad,
            'Responsable': self.Responsable,
            'Comentario': self.Comentario,
            'Pospuesta': self.Pospuesta,
            'FUpdPospuesta': self.FUpdPospuesta
        }