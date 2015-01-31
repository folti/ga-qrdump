Google Authenticator QRCode dumper
==================================

Export OTP keys from a Google Authenticator database as QR codes so you can import them into another app on another device.

Requirements
------------

 * python 2.7 with the sqlite3 module
 * qrcode python module [1]
 * Google Authenticator's SQLite3 database, taken from a rooted device (google it)
 
WARNING!!!
----------

Very crude and no checks for data integrity.

 [1]: https://pypi.python.org/pypi/qrcode
