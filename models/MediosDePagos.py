from database import db

class MedioDePago(db.Model):
    __tablename__ = 'MediosDePagos'
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(255))
    Descripcion = db.Column(db.Text)

    # Definir la relación uno a muchos con Cuotas
    cuotas = db.relationship('Cuota', back_populates='medio_de_pago', lazy=True)
    
    def to_dict(self):
        return {
            'Id': self.Id,
            'Nombre': self.Nombre,
            'Descripcion': self.Descripcion
        }