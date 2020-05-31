from shutil import copyfile
import sys
import os
import subprocess

HOME_PATH = '/home/dmitriy'
client_name = sys.argv[1]
os.chdir(HOME_PATH + '/openvpn-ca')
subprocess.call('source vars && ./revoke-full {}'.format(client_name))

new_cert = HOME_PATH + '/openvpn-ca/keys/crl.pem'
old_cert = '/etc/openvpn/crl.pem'

copyfile(new_cert, old_cert)
