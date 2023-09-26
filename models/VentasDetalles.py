from database import db

class VentaDetalle(db.Model):
    __tablename__ = 'VentasDetalles'
    Id = db.Column(db.Integer, primary_key=True)
    IdVentaEncabezado = db.Column(db.Integer, db.ForeignKey('VentasEncabezados.Id'))
    IdProducto = db.Column(db.Integer, db.ForeignKey('Productos.Id'))
    Cantidad = db.Column(db.Integer)

    # Definir las relaciones con otras tablas
    venta_encabezado = db.relationship('VentaEncabezado', backref='detalle_venta', lazy=True)
    producto = db.relationship("Producto", back_populates="ventas_detalles")
