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
    IdVentaEncabezado = db.Column(db.Integer, db.ForeignKey('VentasEncabezados.Id'), nullable=False)
    IdMedioDePago = db.Column(db.Integer, db.ForeignKey('MediosDePagos.Id'), nullable=False)
    medio_de_pago = db.relationship('MedioDePago', back_populates='cuotas')
    IdUsuario = db.Column(db.Integer, db.ForeignKey('Usuarios.Id'), nullable=False)
    def to_dict(self):
        abono_formatted = "${:,.2f}".format(self.Abono)
        saldo_formatted = "${:,.2f}".format(self.Saldo)
        liquidado_formatted = 'Sí' if self.Liquidado == 1 else 'No'
        return {
            'Id': self.Id,
            'cobrador': self.usuario.Nombre if self.usuario else 'Desconocido',
            'IdVentaEncabezado': self.IdVentaEncabezado,
            'IdMedioDePago': self.IdMedioDePago,
            'IdUsuario': self.IdUsuario,
            'FechaPago': self.FechaPago.strftime('%Y-%m-%d') if self.FechaPago else None,
            'NumCuota': self.NumCuota,
            'Abono': abono_formatted,
            'Saldo': saldo_formatted,
            'Liquidado': liquidado_formatted,
            'FechaLiquidacion': self.FechaLiquidacion
        }