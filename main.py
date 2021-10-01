import os
import asyncio
import argparse
# import csv
# import pandas as pd
import itertools

from os.path import join, dirname
from dotenv import load_dotenv

from init import initialize

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MARKERS = {
    1: "$PEKIO"
}

PACKET_TYPES = {
    1: "RR_L",
    2: "COORD"
}

async def process_lines(pool, line1: list, line2: list):
    query = 'INSERT INTO '
    async with pool.acquire() as connection:
        async with connection.transaction():
            bid = await connection.fetchrow(query, )

    print("RRL", line1)
    print("COORD", line2)

class Parser:
    file_path = None
    chunksize = 10 ** 3

    def __init__(self, file_path: str):
        self.file_path = file_path

    def run(self):
        # Check if file exists
        if not os.path.isfile(self.file_path):
            print("Wrong file path specified!")
            return

        with open(self.file_path) as f:
            for line1, line2 in itertools.zip_longest(*[f]*2):
                if not line1 or not line2:
                    break
                line1 = line1.replace('\n', '').split(',')
                line2 = line2.replace('\n', '').split(',')
                if len(line1) <= 2 or line1[0] not in MARKERS.values() or line1[1] not in PACKET_TYPES.values():
                    continue

                # If COORD has error consider it as bad sample
                if line2[7] != '':
                    continue
                process_lines(line1, line2)
                break
        
        # with pd.read_csv(self.file_path, skiprows=1, delimiter=",", chunksize=self.chunksize, engine="python") as reader:
        #     for chunk in reader:
        #         x = 0

        #         for packet in chunk.itertuples():
        #             print(packet)
                #     if packet[0][0] == MARKERS[1] and packet[0][1] == PACKET_TYPES[1]:
                #         process_rrl_l(packet[0])
                #     elif packet[0][0] == MARKERS[1] and packet[0][1] == PACKET_TYPES[2]:
                #         process_coord(packet[0])
                #     x += 1
                #     if x >= 2:
                #         break
                # break
    
        # int("0x02", 16)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input options')
    parser.add_argument('-p', '--path', type=str, help=r'Path to the file.')
    args = parser.parse_args()

    parser = Parser(file_path=args.path)
    parser.run()
    # print("ZXC", os.environ.get("DATABASE_URL"))
    # loop = asyncio.get_event_loop()

    # initialize(loop)