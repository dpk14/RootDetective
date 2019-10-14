import pyzbar.pyzbar as pyzbar

def read_barcode(img):
    decoded = pyzbar.decode(img, symbols=[pyzbar.ZBarSymbol.QRCODE])
    if decoded == None:
        raise(Exception)
        return
    else:
        barcode=decoded[0]
        data=barcode[0].decode()
        return data
