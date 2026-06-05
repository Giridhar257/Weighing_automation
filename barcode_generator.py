import barcode
from barcode.writer import ImageWriter
import uuid

def generate_barcode():
    code = str(uuid.uuid4())[:8]
    ean = barcode.get('code128', code, writer=ImageWriter())
    filename = f"barcodes/{code}"
    ean.save(filename)
    return code, filename