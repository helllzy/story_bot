from modules.utils import check_gas, check_transaction_status
from data.data import contract_address
from config import RPC

from web3 import Web3
from loguru import logger


class CustomAccount():
    def __init__(self, private_key: int):
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(RPC))
        self.address = self.w3.eth.account.from_key(private_key).address


    def get_transaction_data(self, module: str):

        if module.startswith('request'):
            data = '0x9f678cca'

        match module:
            case 'colorNFT':
                data = '0x40d097c3' + '0' * (64-len(str(self.address)[2:])) + str(self.address)[2:]
            case 'nerzoNFT':
                data = '0x84bb1e42' + '0' * (64-len(str(self.address)[2:])) + str(self.address)[2:] + '0' * 63 + \
                    '1' + '0' * 24 + 'e' * 40 + '0' * 126 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                        '0' * 64 + 'a' + '0' * 88 + 'e' * 40 + '0' * 63 + '1' + '0' * 128

        return data


    @check_gas
    def send_transaction(self, module: str):

        data = self.get_transaction_data(module)

        try:
            last_block = self.w3.eth.get_block('latest')

            max_priority_fee_per_gas = self.get_max_priority_fee_per_gas(block=last_block)

            base_fee = int(last_block['baseFeePerGas'] * 1.3)

            max_fee_per_gas = base_fee + max_priority_fee_per_gas

            tx = {
                'from': self.address,
                'chainId': self.w3.eth.chain_id,
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'to': Web3.to_checksum_address(
                    contract_address[module[8:] + '_address' \
                        if module.startswith('request') else module + '_address']),
                'value': 0,
                'data': data
            }

            tx['gas'] = int(self.w3.eth.estimate_gas(tx) * 1.3)

            sign = self.w3.eth.account.sign_transaction(tx, self.private_key)

            tx_hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)

            check_transaction_status(tx_hash, self.w3)
        
        except Exception as er:
            logger.error(er)


    def get_max_priority_fee_per_gas(self, block: dict) -> int:

        block_number = block['number']

        latest_block_transaction_count = self.w3.eth.get_block_transaction_count(block_number)

        max_priority_fee_per_gas_list = []

        for _id in range(latest_block_transaction_count):
            try:
                transaction = self.w3.eth.get_transaction_by_block(block_number, _id)

                if 'maxPriorityFeePerGas' in transaction:
                    max_priority_fee_per_gas_list.append(transaction['maxPriorityFeePerGas'])
            except:
                continue

        if not max_priority_fee_per_gas_list:
            max_priority_fee_per_gas = self.w3.eth.max_priority_fee
        else:
            max_priority_fee_per_gas_list.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_list[len(max_priority_fee_per_gas_list) // 2]

        return max_priority_fee_per_gas