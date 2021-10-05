import os
import asyncio
import argparse
import asyncpg
import itertools
import re
import math

from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MARKERS = {
    '$PEKIO': 1
}

PACKET_TYPES = {
    'RR_L': 1,
    'COORD': 2 
}

async def init_async_cursor(dsn):
    pool = await asyncpg.create_pool(dsn)
    return pool

async def insert_packets(pool, rrl_packet: str, coord_packet: str):
    if not rrl_packet or not coord_packet:
        return 

    rrl_packet = rrl_packet.replace('\n', '').split(',')
    coord_packet = coord_packet.replace('\n', '').split(',')
    if len(rrl_packet) <= 2 or rrl_packet[0] not in MARKERS.keys() or rrl_packet[1] not in PACKET_TYPES.keys():
        return

    # If COORD has error consider it as bad sample
    if coord_packet[7] != '':
        return

    rrl_marker, coord_marker = rrl_packet[0], coord_packet[0]
    rrl_packet_type, coord_packet_type = rrl_packet[1], coord_packet[1]
    rrl_sequence_number, coord_sequence_number = rrl_packet[2], coord_packet[2]

    # Here we assume sequence number of RRL_L and COORD should match
    if rrl_sequence_number != coord_sequence_number:
        raise "Sequence numbers of RR_L and COORD does not match!"

    rrl_device_id, coord_device_id = int(rrl_packet[3], 16), int(coord_packet[3], 16)

    anchors, device_timestamp, moving_indicators = '', '', ''
    for field in rrl_packet[4:]:
        match = re.match(r'^\d{9}$', field)
        if match:
            device_timestamp = field
            continue
        if device_timestamp:
            moving_indicators += ',' + field if moving_indicators else field
        else:
            anchors += ',' + field if anchors else field

    x, y, z, error_message, coord_timestamp = coord_packet[4], coord_packet[5], coord_packet[6], coord_packet[7], coord_packet[8]
    async with pool.acquire() as connection:
        async with connection.transaction():
            device_packet = await connection.fetchval(
                '''SELECT id FROM rr_l 
                WHERE marker_id = $1 AND packet_type_id = $2 AND sequence_number = $3 AND device_id = $4 AND created_at = $5;''', 
                MARKERS[rrl_marker], 
                PACKET_TYPES[rrl_packet_type], 
                int(rrl_sequence_number), 
                int(rrl_device_id), 
                datetime.fromtimestamp(int(device_timestamp)))
            
            # If the device packet record found we'll pass it
            if device_packet:
                return

            await connection.execute(
                '''INSERT INTO rr_l (marker_id, packet_type_id, sequence_number, device_id, anchors, created_at, moving) 
                VALUES ($1, $2, $3, $4, $5, $6, $7);''', 
                MARKERS[rrl_marker], 
                PACKET_TYPES[rrl_packet_type], 
                int(rrl_sequence_number), 
                int(rrl_device_id), 
                anchors, 
                datetime.fromtimestamp(float(device_timestamp)), 
                moving_indicators
            )

            await connection.execute(
                '''INSERT INTO coord (marker_id, packet_type_id, device_sequence_number, device_tag_id, x, y, z, error_message, created_at) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);''', 
                MARKERS[coord_marker], 
                PACKET_TYPES[coord_packet_type], 
                int(coord_sequence_number), 
                int(coord_device_id), 
                x, 
                y,
                z,
                error_message,
                datetime.fromtimestamp(float(coord_timestamp))
            )

async def process_devices(pool, devices: dict):
    total_points_in_circle = 0
    for device_id, device_data in devices.items():
        async with pool.acquire() as connection:
            async with connection.transaction():
                device_coondinates = await connection.fetch(
                    '''SELECT x, y, z FROM coord WHERE device_tag_id = $1;''',
                    device_id
                )

        dcp = device_data['current_position']
        for coord in device_coondinates:
            # Set initial coordinates of the device
            if dcp['x'] == 0 and dcp['y'] == 0 and dcp['z'] == 0:
                dcp['x'], dcp['y'], dcp['z'] = coord['x'], coord['y'],  coord['z']
            
            # Count the positions inside the circle with center (30,50) and radius 5m. 
            if dcp['x'] >= 25 and dcp['x'] <= 35 and dcp['y'] >= 45 and dcp['y'] <= 55:
                device_data['points_in_circle'] += 1

            moved, moved_x, moved_y, moved_z = False, 0.0, 0.0, 0.0
            if dcp['x'] != coord['x']:
                moved = True
                moved_x = abs(float(dcp['x']) - float(coord['x']))
            if dcp['y'] != coord['y']:
                moved = True
                moved_y = abs(float(dcp['y']) - float(coord['y']))
            if dcp['z'] != coord['z']:
                moved = True
                moved_z = abs(float(dcp['z']) - float(coord['z']))
            if moved:
                dcp['x'], dcp['y'], dcp['z'] = coord['x'], coord['y'],  coord['z']
                device_data['distance_moved'] += math.sqrt(moved_x**2 + moved_y**2 + moved_z**2)
        total_points_in_circle += device_data['points_in_circle']
    return devices, total_points_in_circle

async def calculate_data(pool):
    async with pool.acquire() as connection:
        async with connection.transaction():
            rrl_packets = await connection.fetch(
                '''SELECT id, marker_id, packet_type_id, sequence_number, device_id, anchors, created_at, moving 
                    FROM rr_l;'''
            )

    devices = {}
    for rrl in rrl_packets:
        for i in rrl['moving'].split(','):
            lsb = int(i, 16)
            #  If the least significant bit in the moving indication field is 1, then
            # consider the tag not moving, otherwise it is moving. 
            if lsb & -lsb > 0:
                continue
        devices[rrl['device_id']] = {
            'distance_moved': 0.0,
            'points_in_circle': 0,
            'current_position': {
                'x': 0.00,
                'y': 0.00,
                'z': 0.00,
            }
        }

    devices, total_points_in_circle = await process_devices(pool, devices)
    for k, v in devices.items():
        print(f"DeviceID: {k}, Distance moved: {v['distance_moved']}, Points in the circle: {v['points_in_circle']}")
    
    print(f"Total points in circle: {total_points_in_circle}")

class Parser:
    file_path = None
    chunksize = 10 ** 3

    def __init__(self, file_path: str):
        self.file_path = file_path

        dsn = os.environ.get("DATABASE_URL")
        self.loop = asyncio.get_event_loop()
        self.pool = self.loop.run_until_complete(
            init_async_cursor(dsn)
        )

    def run(self):
        # Check if file exists
        if not os.path.isfile(self.file_path):
            print("Wrong file path specified!")
            return

        with open(self.file_path) as f:
            for rrl_packet, coord_packet in itertools.zip_longest(*[f]*2):
                self.loop.run_until_complete(insert_packets(self.pool, rrl_packet, coord_packet))

        self.loop.run_until_complete(calculate_data(self.pool))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input options')
    parser.add_argument('-p', '--path', type=str, help=r'Path to the file.')
    args = parser.parse_args()

    parser = Parser(file_path=args.path)
    parser.run()