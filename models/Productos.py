from database import db

class Producto(db.Model):
    __tablename__ = 'Productos'
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(255))
    Descripcion = db.Column(db.String(255))
    ValorCosto = db.Column(db.Numeric(10, 2))
    ValorVenta = db.Column(db.Numeric(10, 2))
    ValorInicial = db.Column(db.Numeric(10, 2))
    ValorCuota = db.Column(db.Numeric(10, 2))
    NumCuotas = db.Column(db.Integer)
    ConfActivo = db.Column(db.Boolean)
    ConfPorUtilidad = db.Column(db.BigInteger)
    FechaRegistro = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Definir la relación uno a muchos con VentasDetalles
    ventas_detalles = db.relationship("VentaDetalle", back_populates="producto")