from config import RPC, MAX_GWEI

from time import sleep, time
from functools import wraps
from random import randint

from loguru import logger
from web3 import Web3


def sleeping(secs, text=None, color=None) -> None:
    if text:
        info(text, color)

    sleep(randint(*secs))


def info(text, color="white") -> None:
    logger.opt(colors=True).info(f'<{color}>{text}</{color}>')


def check_gas(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        while True:
            try:
                w3 = Web3(Web3.HTTPProvider(RPC))
                gas_price = round(w3.from_wei(w3.eth.gas_price, 'gwei'), 2)

                if gas_price > MAX_GWEI:
                    logger.warning(
                        f"Story gas`s {gas_price} | sleep 30 seconds"
                        )
                    sleep(30)
                else:
                    break

            except:
                pass

        return func(*args, **kwargs)
    return wrapper


def check_transaction_status(tx_hash, w3):
    info(f'checking tx_status: https://testnet.storyscan.xyz/tx/{tx_hash.hex()}', 'blue')

    start_time_stamp = int(time())

    while True:
        status = ''

        sleep(5)

        try:

            status = w3.eth.get_transaction_receipt(tx_hash)["status"]

            match status:
                case 0:
                    logger.critical('transaction failed')
                    break
                case 1:
                    logger.success('transaction success')
                    break

        except Exception as er:
            time_stamp = int(time())

            if time_stamp-start_time_stamp > 120:
                logger.error('didn`t get the tx_status')
                break
            else:
                logger.error(er)