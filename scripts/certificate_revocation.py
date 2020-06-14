from shutil import copyfile

new_cert = HOME_PATH + '/openvpn-ca/keys/crl.pem'
old_cert = '/etc/openvpn/crl.pem'

copyfile(new_cert, old_cert)
