import configparser
import subprocess
import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logging.info('Loading config...')
config = configparser.ConfigParser()
config.read('/opt/dell-custom-fan-curve/config.ini')

host = config['HOSTCONFIG']['Host']
username = config['HOSTCONFIG']['Username']
password = config['HOSTCONFIG']['Password']

curve = []
default_speed = int(config['FANCONTROL']['default'])

for key in config['FANCONTROL']:
    if key != 'default':
        curve.append((int(key),int(config['FANCONTROL'][key])))

max_disk_temp = int(config['DRIVE']['max_temp'])
logging.info('Done.')

logging.info('Enabling manual fan mode')
cmd_enable_fan_control = ['/usr/bin/ipmitool', '-I', 'lanplus', '-U', username, '-P', password, '-H', host, 'raw', '0x30', '0x30', '0x01', '0x00']
process = subprocess.run(cmd_enable_fan_control, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
if process.returncode > 0:
    print(process.stderr)
    exit(process.returncode)
logging.info('Done.')

logging.info('Starting Monitoring.')
while True:
    max_temp = 0
    disk_temp = 0
    sys_temp = 0
    _speed = default_speed

    logging.info('Retrieving server temp')
    cmd_get_server_temp = ['/usr/bin/ipmitool', '-I', 'lanplus', '-U', username, '-P', password, '-H', host, 'sdr', 'type', 'temperature']
    process = subprocess.run(cmd_get_server_temp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if process.returncode > 0:
        logging.error(process.stderr)
        exit(process.returncode)
    for lines in list(filter(None,process.stdout.split('\n'))):
        curr_temp = int(str.strip(lines.split('|')[4]).split(' ')[0])
        if curr_temp > max_temp:
            max_temp = curr_temp
    sys_temp = max_temp
    logging.info('Done.')

    logging.info('Retrieving disks temp')
    for d in config['DRIVE']['list'].split(','):
        drive = '/dev/%(drive)s' % { 'drive': str(d) }
        cmd_get_drive_temp = ' | '.join([' '.join(['/usr/sbin/smartctl', '-A', drive, '-d', 'megaraid,0']), ' '.join(['grep', '"Current Drive Temperature"'])])
        process = subprocess.run(cmd_get_drive_temp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        if process.returncode > 0:
            logging.error(process.stderr)
            exit(process.returncode)
        for lines in list(filter(None,process.stdout.split('\n'))):
            _disk_temp = int(lines.split(':')[1].strip().split(' ')[0])
            logging.info('Drive %(drive)s is at %(disk_temp)s °C.' % {'drive': drive, 'disk_temp': _disk_temp})
        if _disk_temp > disk_temp:
            disk_temp = _disk_temp
    logging.info('Done.')

    logging.info('Checking all temps')
    speed = hex(default_speed)
    if disk_temp >= max_disk_temp:
        logging.warning('Disk is at %(disk_temp)s ! Enabling turbo fan speed.' % {'disk_temp': str(disk_temp)})
        max_temp = disk_temp
        speed = hex(95)
    else:
        for fan_speed in curve:
            if max_temp >= fan_speed[0]:
                if fan_speed[1] > _speed:
                    speed = hex(fan_speed[1])
                    _speed = fan_speed[1]
    logging.info('Done.')

    logging.info('Server is at %(max_temp)s °C [System : %(sys_temp)s °C | Disk : %(disk_temp)s °C]. Setting fan speed to %(_speed)s percent.' % {'max_temp': str(max_temp), '_speed': str(_speed), 'disk_temp': str(disk_temp), 'sys_temp': str(sys_temp)})
    cmd_set_fan_speed = ['/usr/bin/ipmitool', '-I', 'lanplus', '-U', username, '-P', password, '-H', host, 'raw', '0x30', '0x30', '0x02', '0xff', speed]
    process = subprocess.run(cmd_set_fan_speed, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if process.returncode > 0:
        logging.error(process.stderr)
        exit(process.returncode)
    logging.info('Done.')

    sleep(10)
