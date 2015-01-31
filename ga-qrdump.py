#!/usr/bin/env python

import sys
import os
import re
import sqlite3
import qrcode
import codecs


db = 'databases'
# https://code.google.com/p/google-authenticator/wiki/KeyUriFormat

def make_qrimage(url, filename):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    print qr.print_ascii()
    print qr.print_ascii(invert=True)
    print qr.print_tty()
    img = qr.make_image()
    img.save(filename)


def main():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for row in c.execute('''SELECT email, secret, issuer, original_name FROM accounts'''):
        qrurl = "otpauth://totp/%s?secret=%s&issuer=%s" % (row[0], row[1], row[2] if row[2] is not None else row[3])
        print qrurl
        outname = re.sub('[:/]', '_', row[0]) + '.png'
        print outname
        make_qrimage(qrurl, outname)

if __name__ == '__main__':
    main()
