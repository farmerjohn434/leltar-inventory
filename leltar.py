from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
import csv
from io import StringIO
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/qrcodes'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial = db.Column(db.String(100), unique=True)
    user = db.Column(db.String(100))
    location = db.Column(db.String(100))
    status = db.Column(db.String(50))
    note = db.Column(db.String(200))
    inventory_number = db.Column(db.String(100), unique=True)

    def qr_code_path(self):
        return f"{app.config['UPLOAD_FOLDER']}/{self.inventory_number}.png"

@app.route('/')
def index():
    devices = Device.query.all()
    return render_template('index.html', devices=devices)

@app.route('/add', methods=['POST'])
def add():
    try:
        data = request.form
        inventory_number = data.get('inventory_number')
        serial = data.get('serial')

        if not inventory_number or not serial:
            return "Hiányzó kötelező mező!", 400

        if Device.query.filter_by(inventory_number=inventory_number).first():
            return "Ez a leltári szám már létezik!", 400

        if Device.query.filter_by(serial=serial).first():
            return "Ez a sorozatszám már létezik!", 400

        device = Device(
            category=data.get('category'),
            brand=data.get('brand'),
            model=data.get('model'),
            serial=serial,
            user=data.get('user'),
            location=data.get('location'),
            status=data.get('status'),
            note=data.get('note'),
            inventory_number=inventory_number
        )
        db.session.add(device)
        db.session.commit()
        generate_qr(device)
        return redirect(url_for('index'))

    except Exception as e:
        return f"Hiba történt a hozzáadás során: {str(e)}", 500

def generate_qr(device):
    qr = qrcode.make(
        f"Inventory #{device.inventory_number}\n{device.category} - {device.brand} {device.model}"
    )
    qr.save(device.qr_code_path())

@app.route('/delete/<int:id>')
def delete(id):
    device = Device.query.get(id)
    if device and os.path.exists(device.qr_code_path()):
        os.remove(device.qr_code_path())
    db.session.delete(device)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export_csv():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Category', 'Brand', 'Model', 'Serial', 'User', 'Location', 'Status', 'Note', 'Inventory Number'])
    for d in Device.query.all():
        cw.writerow([
            d.id, d.category, d.brand, d.model,
            d.serial, d.user, d.location,
            d.status, d.note, d.inventory_number
        ])
    output = si.getvalue()
    return send_file(StringIO(output), mimetype='text/csv', as_attachment=True, download_name='inventory.csv')

@app.route('/export_excel')
def export_excel():
    devices = Device.query.all()
    df = pd.DataFrame([{
        'Felhasználó': d.user,
        'Kategória': d.category,
        'Márka': d.brand,
        'Modell': d.model,
        'Sorozatszám': d.serial,
        'Hely': d.location,
        'Állapot': d.status,
        'Megjegyzés': d.note,
        'Leltári szám': d.inventory_number
    } for d in devices])

    file_path = "static/inventory_export.xlsx"
    df.to_excel(file_path, index=False, engine='openpyxl')
    return send_file(file_path, as_attachment=True)

@app.route('/import_excel', methods=['POST'])
def import_excel():
    file = request.files.get('file')
    if not file:
        return "Nincs feltöltött fájl.", 400

    try:
        df = pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        return f"Hiba az Excel fájl olvasásakor: {e}", 400

    for _, row in df.iterrows():
        if Device.query.filter_by(inventory_number=row['Leltári szám']).first():
            continue

        if Device.query.filter_by(serial=row['Sorozatszám']).first():
            continue

        device = Device(
            user=row['Felhasználó'],
            category=row['Kategória'],
            brand=row['Márka'],
            model=row['Modell'],
            serial=row['Sorozatszám'],
            location=row['Hely'],
            status=row['Állapot'],
            note=row.get('Megjegyzés', ''),
            inventory_number=row['Leltári szám']
        )
        db.session.add(device)

    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
         db.create_all()
    app.run()
