import random
import string

from pathlib import Path


def get_client_cert_contents():
    return Path('certs/avery.redbuttegarden.org.crt', encoding='utf-8').read_text()


def get_client_key_contents():
    return Path('certs/avery.redbuttegarden.org.key', encoding='utf-8').read_text()


def get_random_characters(num=6):
    return ''.join(random.choices(string.ascii_lowercase, k=num))


def modify_contents(contents, cert, key):
    """Make changes to contents of OVPN config file contents."""
    remote_url_line = contents[3].split()
    remote_url = remote_url_line[1]
    remote_url = get_random_characters() + '.' + remote_url
    remote_url_line[1] = remote_url
    contents[3] = ' '.join(remote_url_line) + '\n'

    contents.insert(33, cert)
    contents.insert(35, key)

    return contents


def read_ovpn_config():
    with open('aws_gateway.ovpn', 'r') as ovpn_config:
        lines = ovpn_config.readlines()

    return lines


def write_ovpn_config(contents):
    with open('aws_gateway.ovpn', 'w+') as ovpn_config:
        ovpn_config.writelines(contents)


def prepare_config():
    client_cert = '<cert>\n' + get_client_cert_contents() + '\n</cert>\n'
    client_key = '<key>\n' + get_client_key_contents() + '\n</key>'
    config = read_ovpn_config()
    config = modify_contents(config, client_cert, client_key)
    write_ovpn_config(config)


if __name__ == '__main__':
    prepare_config()
