"""
Automatically backup the Red Butte Garden website database.

This script first provisions the VPN gateway in AWS then passes the configuration files to a docker container running as
an OpenVPN client. A second docker container connects to the VPN to retrieve the database dump from the AWS RDS
instance.
"""
import datetime
import logging
import os
import subprocess
import time
from pathlib import Path

from dotenv import load_dotenv
from vpn_config import prepare_config

load_dotenv(os.path.join(Path(__file__).parent.absolute(), 'creds.env'))


def destroy_aws_vpn_gateway():
    """
    Take down the AWS VPN gateway after we're done with it.
    """
    logging.info('Destroying AWS VPN Gateway...')
    try:
        subprocess.run([os.path.join(Path(__file__).parent.absolute(), 'scripts/aws_vpn_deletion.sh')], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f'[!] Error!: {e}')


def provision_aws_vpn_gateway():
    """
    Requests the association of the RDS subnet to an existing AWS
    Client VPN Endpoint
    """
    logging.info('Provisioning AWS VPN Gateway...')
    try:
        subprocess.run([os.path.join(Path(__file__).parent.absolute(), 'scripts/aws_vpn_creation.sh')], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f'[!] Error!: {e}')


def run_db_dump_container():
    """
    Docker container that will connect to AWS RDS thru
    the VPN container and dump the database.

    The IP of the RDS instance is hard-coded because there were issues
    with resolving DNS within the container when trying to use the
    RDS endpoint URL.

    The AWS VPN Gateway can sometimes take over an hour before it will
    allow client connections so we allow multiple attempts between
    pauses.
    """
    logging.info('Running database container using VPN network...')
    todays_date = datetime.date.today().strftime('%m-%d-%Y')
    with open(os.path.join(Path(__file__).parent.absolute(), 'backups/' + todays_date + '.sql'), 'w+') as db_dump:
        attempts = 1
        while attempts <= 6:
            logging.info(f'\t...attempt number {str(attempts)}')
            try:
                subprocess.run(['docker', 'run', '--rm', '--net=container:vpn-client', '-e',
                                'PGPASSWORD=' + os.getenv('PGPASSWORD'), 'postgres:12.3', 'pg_dump', '-h',
                                os.getenv('PGHOST'), '-U', os.getenv('PGUSERNAME'), '-d', os.getenv('PGDB')],
                               check=True, stdout=db_dump)
                logging.info('\t...Success!')
                return
            except subprocess.CalledProcessError as e:
                attempts += 1
                logging.error(f'[!] Error!: {e}')
                logging.info('Sleeping for 10 minutes before trying again...')
                time.sleep(600)


def start_vpn_container():
    """
    Start up the docker container that will run as our OpenVPN client.
    """
    logging.info('Starting VPN client container...')
    try:
        subprocess.run(['docker', 'run', '-d', '--name', 'vpn-client', '--cap-add=NET_ADMIN', '--device',
                        '/dev/net/tun', '-v', str(Path(__file__).parent.absolute()) + ':/vpn', 'vpn', '--config',
                        '/vpn/aws_gateway.ovpn', '--auth-nocache'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f'[!] Error!: {e}')


def destroy_vpn_container():
    """Stop and remove any running VPN client containers"""
    logging.info('Cleaning up containers...')
    subprocess.run(['docker', 'stop', 'vpn-client'])
    subprocess.run(['docker', 'rm', 'vpn-client'])


def build_vpn_container():
    """
    Builds an image using the Dockerfile contained alongside this script.
    Tags the container that will run the VPN client as 'vpn'.
    """
    logging.info('Building VPN client container...')
    try:
        subprocess.run(['docker', 'build', '.', '-t', 'vpn'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f'[!] Error!: {e}')


def main():
    logging.basicConfig(filename=os.path.join(Path(__file__).parent.absolute(), 'main.log'), level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    provision_aws_vpn_gateway()
    logging.info('Modifying VPN config file...')
    prepare_config()
    logging.info('Creating copy of VPN config file that can be shared with containers...')

    # Wait 10 minutes for the VPN Gateway to be ready to accept connections
    logging.info('Sleeping for ten minutes to wait for AWS VPN Gateway to be ready...')
    time.sleep(600)

    build_vpn_container()
    start_vpn_container()
    run_db_dump_container()
    destroy_aws_vpn_gateway()
    destroy_vpn_container()

    logging.info('Done!')


if __name__ == '__main__':
    main()