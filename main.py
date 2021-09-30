import os
import asyncio
import argparse
import csv

from os.path import join, dirname
from dotenv import load_dotenv

from init import initialize

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Parser:
    file_path = None

    def __init__(self, file_path: str):
        self.file_path = file_path

    def run(self):
        # Check if file exists
        if not os.path.isfile(self.file_path):
            print("Wrong file path specified!")
            return
    
        with open(self.file_path) as csvDataFile:
            # read file as csv file 
            csvReader = csv.reader(csvDataFile)
            # for every row, print the row
            for row in csvReader:
                print(row)
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input options')
    parser.add_argument('-p', '--path', type=str, help=r'Path to the file.')
    args = parser.parse_args()

    print("PATH", args.path)

    parser = Parser(file_path=args.path)
    parser.run()
    # print("ZXC", os.environ.get("DATABASE_URL"))
    # loop = asyncio.get_event_loop()

    # initialize(loop)