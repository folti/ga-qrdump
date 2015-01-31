#!/usr/bin/env python

import sys
import os
import re
import sqlite3
import qrcode
import codecs
import argparse


default_db = 'databases'
# https://code.google.com/p/google-authenticator/wiki/KeyUriFormat


def make_qrimage(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    return qr


def query_db(args):
    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    qry = '''SELECT _id, email, secret, issuer, original_name FROM accounts '''
    if args.id:
        qry += ''' WHERE _id={id}'''.format(id=args.id)
    qry += ''' ORDER BY _id'''
    resp = c.execute(qry)
    return resp


def list_entries(args):
    resp = query_db(args)
    fmt = "% 3s: %-20s: %s"
    title = fmt % ('ID', 'Issuer', 'e-mail')
    print title
    print '-' * len(title)
    for row in resp:
        print fmt % (row[0], row[3] if row[3] is not None else row[4], row[1])


def process_db(args):
    if args.list_entries:
        return list_entries(args)

    isatty = os.isatty(sys.stdout.fileno())
    if not isatty:
        # Stdout is not a terminal. Force it to be utf-8.
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    resp = query_db(args)
    for row in resp:
        qrurl = "otpauth://totp/%s?secret=%s&issuer=%s" % (row[1], row[2], row[3] if row[3] is not None else row[4])
        if args.url_only:
            print qrurl
        qr = make_qrimage(qrurl)

        if args.tty:
            print "%s: %s" % (row[3] if row[3] is not None else row[4], row[1])
            if isatty:
                qr.print_tty()
            else:
                qr.print_ascii(out=sys.stdout, invert=True)
            print

        if args.png:
            outname = re.sub('[:/]', '_', row[1]) + '.png'
            print outname
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
    if not os.path.exists(default_db):
        print "Database file '%s' not exists."
        sys.exit(1)

    process_db(args)


if __name__ == '__main__':
    main()
