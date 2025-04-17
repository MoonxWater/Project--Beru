import qrcode, os
import qrcode.constants
from PIL import Image

def qr():
    query = input('Enter text to convert: ')

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(query)
    qr.make(fit=True)
    img = qr.make_image(fill_color='blue', back_color='white')
    img.save("query.png")

    os.startfile('query.png')

if __name__ == '__main__':
    qr()