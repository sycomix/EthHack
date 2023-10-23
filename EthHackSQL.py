#!/usr/bin/python3
import sha3
import multiprocessing
import psutil
import pyodbc
import os
import random
from ecdsa import SigningKey, SECP256k1
from web3 import Web3, KeepAliveRPCProvider


# Point to RPC server
ethNode = 'localhost'


# Configure SQL connection parameters
# https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
# {ODBC Driver 13 for SQL Server}
def sql_upload(private,address,balance):
    try:
        cnxn = pyodbc.connect(
            driver='',
            server='',
            database='',
            uid='',
            pwd=''
        )
        cursor = cnxn.cursor()
        values = "('{0}','{1}','{2}')".format(private, address, balance)
        query = f"BEGIN INSERT INTO Unverified (PRIVATE, ADDRESS, BALANCE) VALUES {values} END;"
        cursor.execute(query)
        cnxn.commit()
        cursor.close()
        cnxn.close()
    except:
        with open(address, 'w') as f:
            f.write("PRIVATE: {0}\nADDRESS: {1}\nBALANCE: {2}\n".format(private, address, balance))
        f.close()


def ethhack():
    web3 = Web3(KeepAliveRPCProvider(host=ethNode, port='8545'))
    while True:
        keccak = sha3.keccak_256()
        private = SigningKey.generate(curve=SECP256k1)
        public = private.get_verifying_key().to_string()
        keccak.update(public)
        address = f"0x{keccak.hexdigest()[24:]}"
        try:
            balance = web3.eth.getBalance(address)
        except:
            balance = -1
        if balance != 0:
            sql_upload(private.to_string().hex(),address,balance)


if __name__ == "__main__":
    cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cores)
    parent = psutil.Process()
    if os.name == 'nt':
        parent.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        for child in parent.children():
            child.nice(psutil.IDLE_PRIORITY_CLASS)
    else:
        parent.nice(10)
        for child in parent.children():
            child.nice(19)
    [pool.apply_async(ethhack) for _ in range(cores)]
    pool.close()
    pool.join()
