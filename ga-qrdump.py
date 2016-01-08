#!/usr/bin/env python
from __future__ import print_function

import sys
import os
import re
import sqlite3
import qrcode
import codecs
import argparse
from urllib import quote, quote_plus


default_db = 'databases'
# https://code.google.com/p/google-authenticator/wiki/KeyUriFormat


def make_qrimage(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    return qr


def query_db(args):
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    qry = '''SELECT * FROM accounts '''
    if args.id:
        qry += ''' WHERE _id={id}'''.format(id=args.id)
    qry += ''' ORDER BY _id'''
    resp = c.execute(qry)
    return resp


def list_entries(args):
    resp = query_db(args)
    fmt = "% 3s: %-20s: %s"
    title = fmt % ('ID', 'Issuer', 'e-mail')
    print("%s\n%s" % (title, '-' * len(title)))
    for row in resp:
        print(fmt % (row['_id'], row['issuer'] if row['issuer'] is not None else row['original_name'], row['email']))


def create_otpauth_url(atype, secret, email, **kwds):
    if isinstance(atype, int):
        if atype == 0:
            atype = 'totp'
        elif atype == 1:
            atype == 'hotp'
        else:
            raise ValueError("Invalid OTP type '%s'" % atype)

    url = "otpauth://" + atype + "/" + quote(email, safe="/@") + "?secret=" + secret

    if atype == 'totp':
        if 'period' in kwds:
            url += '&period=' + kwds['period']

        if 'digits' in kwds:
            url += '&digits=' + kwds['digits']
    elif atype == 'hotp':
        if 'counter' in kwds:
            url +='&counter=' + kwds['counter']

    if 'issuer' in kwds:
        url += "&issuer=" + quote_plus(kwds['issuer'])

    return url

def process_db(args):
    if args.list_entries:
        return list_entries(args)

    isatty = os.isatty(sys.stdout.fileno())
    if not isatty:
        # Stdout is not a terminal. Force it to be utf-8.
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    resp = query_db(args)
    for row in resp:
        qrurl = create_otpauth_url(atype=row['type'], secret=row['secret'], email=row['email'],
                                   issuer=row['issuer'] if row['issuer'] is not None else row['original_name'],
                                   counter=row['counter'])
        if args.url_only:
            print(qrurl)
        qr = make_qrimage(qrurl)

        if args.tty:
            print("%s: %s" % (row['issuer'] if row['issuer'] is not None else row['original_name'], row['email']))
            if isatty:
                qr.print_tty()
                print()
                raw_input('Press enter to continue...')
            else:
                qr.print_ascii(out=sys.stdout, invert=True)
                print()

        if args.png:
            outname = re.sub('[:/]', '_', row['email']) + '.png'
            print(outname)
            img = qr.make_image()
            img.save(outname)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--db", "--ga-db", help="Name of the Google Authenticator database file")
    parser.add_argument("--list-entries", action="store_true", help="List the entries in the database file.")
    parser.add_argument("--png", action="store_true", help="Save generated codes as PNG files.")
    parser.add_argument("--tty", action="store_true", help="Dump entries to console as ANSI graphics")
    parser.add_argument("--url-only", action="store_true", help="Only print the otpauth:// URLs.")
    parser.add_argument("--id", help="Dump only the one which has the id")

    args = parser.parse_args()
    if not args.db:
        args.db = default_db
    if not os.path.exists(args.db):
        print("Database file '%s' not exists." % args.db)
        sys.exit(1)

    process_db(args)


if __name__ == '__main__':
    main()
