from config import RPC, MAX_GWEI

from asyncio import sleep
from time import time
from functools import wraps
from random import randint

from loguru import logger
from web3 import Web3


logger.add('data/logs.log')


async def sleeping(secs, text=None, color=None) -> None:
    if text:
        await info(text, color)

    await sleep(randint(*secs))


async def info(text, color: str="white") -> None:
    logger.opt(colors=True).info(f'<{color}>{text}</{color}>')


def check_gas(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        while True:
            try:
                w3 = Web3(Web3.HTTPProvider(RPC))
                gas = w3.eth.gas_price
                gas_price = round(w3.from_wei(gas, 'gwei'), 2)

                if gas_price > MAX_GWEI:
                    logger.warning(
                        f"Story gas`s {gas_price} | sleep 30 seconds"
                        )
                    await sleep(30)
                else:
                    break

            except Exception as er:
                print(er)

        return await func(*args, **kwargs)
    return wrapper


async def check_transaction_status(tx_hash, w3, id):
    await info(f'[{id}] | Checking tx status: https://testnet.storyscan.xyz/tx/{Web3.to_hex(tx_hash)}', 'blue')

    start_time_stamp = int(time())

    while True:
        status = ''

        await sleep(15)

        try:

            status = await w3.eth.get_transaction_receipt(tx_hash)

            match status["status"]:
                case 0:
                    logger.critical(f'[{id}] | Transaction failed')
                    break
                case 1:
                    logger.success(f'[{id}] | Transaction success')
                    break

        except Exception as er:
            time_stamp = int(time())

            if time_stamp-start_time_stamp > 120:
                logger.error(f'[{id}] | Didn`t get the tx_status')
                break
            else:
                logger.error(er)
