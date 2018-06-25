import os
import logging
import argparse
from paramiko import SSHClient, AutoAddPolicy

LOGGER = logging.getLogger()


def connect_to_host(host):
    ssh_connection = SSHClient()
    ssh_connection.set_missing_host_key_policy(AutoAddPolicy())
    ssh_connection.connect(hostname=host)
    return ssh_connection


def pull_down_pubkey(ssh_connection, host):
    sftp_client = ssh_connection.open_sftp()
    sftp_client.get('.ssh/id_rsa.pub', '{}'.format(str(host)))
    sftp_client.close()


def write_to_authorized_keys(host):
    with open('authorized_keys', 'a+') as auth_keys:
        with open(host, 'r') as key:
            ssh_key = key.read()
            auth_keys.write(ssh_key)


def upload_authorized_keys_file(ssh_connection):
    sftp_client = ssh_connection.open_sftp()
    sftp_client.put('authorized_keys', '.ssh/authorized_keys')


def parse_args():
    parser = argparse.ArgumentParser(description='Enable ssh access for a list of hosts',
                                     usage='%(prog)s filename.txt .ssh/id_rsa.pub')
    parser.add_argument('file_with_hosts', type=argparse.FileType('r'),
                        help="A list of hostnames that you'd like to add keys to.")
    parser.add_argument('default_keys', type=argparse.FileType('r'),
                        help="File with default keys that should remain on remote hosts")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    hosts = [host for host in args.file_with_hosts.readlines()]

    with open('authorized_keys', 'w') as auth_keys:
        auth_keys.write(args.default_keys.read())
sirrrrrrrrrr
    for server_ip in hosts:
        connection = connect_to_host(server_ip)
        connection.exec_command("ssh-keygen -t rsa -f .ssh/id_rsa -N ''")
        pull_down_pubkey(connection, server_ip)
        write_to_authorized_keys(server_ip)
        try:
            os.remove(server_ip)
        except IOError:
            LOGGER.warning('No key file found for host {}'.format(server_ip))

    for server_ip in hosts:
        connection = connect_to_host(server_ip)
        upload_authorized_keys_file(connection)

    os.remove('authorized_keys')
