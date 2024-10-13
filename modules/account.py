from modules.utils import check_gas, check_transaction_status, logger
from data.data import contract_address, USE_PROXY
from config import RPC

from random import randint

from web3 import AsyncWeb3
from web3.middleware import async_geth_poa_middleware


class CustomAccount():
    def __init__(self, wallet, id):
        self.private_key = wallet['private_key']
        self.id = id

        if USE_PROXY:
            proxy = wallet["proxy"]
            _proxy = f'{proxy[proxy.find(":")+6:]}@{proxy[:proxy.find(":")+5]}'
            request_kwargs = {"proxy": f"http://{_proxy}"}

        self.w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(RPC),
            middlewares=[async_geth_poa_middleware],
            request_kwargs=request_kwargs
        )

        self.address = self.w3.eth.account.from_key(self.private_key).address


    async def get_transaction_data(self, module: str, value=0):

        if module.startswith('request'):
            data = '0x9f678cca'

        elif 'NFT' in module:
            data = '0x84bb1e42' + '0' * (64-len(str(self.address)[2:])) + str(self.address)[2:] + '0' * 63

            match module:
                case 'nerzoNFT_story':
                    data += str(randint(1, 5)) + '0' * 24 + 'e' * 40 + '0' * 126 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                        '0' * 64 + 'a' + '0' * 88 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                case 'nerzoNFT_highway':
                    data += str(randint(1, 5)) + '0' * 24 + 'e' * 40 + '0' * 126 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                        '0' + 'f' * 64 + '0' * 88 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                case 'nerzoNFT_storylliad':
                    data += str(randint(1, 5)) + '0' * 24 + 'e' * 40 + '0' * 126 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                        '0' + 'f' * 64 + '0' * 88 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                case 'morkieNFT_mystory':
                    data += '1' + '0' * 24 + 'e' * 40 + '0' * 49 + '0b1a2bc2ec5' + '0' * 66 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                        '0' * 64 + '1' + '0' * 49 + '0b1a2bc2ec5' + '0' * 28 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                    value = 0.05
                case 'morkieNFT_story':
                    data += '1' + '0' * 24 + 'e' * 40 + '0' * 49 + '16345785d8a' + '0' * 66 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                        '0' * 64 + '1' + '0' * 49 + '16345785d8a' + '0' * 28 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                    value = 0.1

        else:
            match module:
                case 'color':
                    data = '0x40d097c3' + '0' * (64-len(str(self.address)[2:])) + str(self.address)[2:]

        return data, int(value*1e18)


    @check_gas
    async def send_transaction(self, module: str):

        data, value = await self.get_transaction_data(module)

        try:
            last_block = await self.w3.eth.get_block('latest')

            max_priority_fee_per_gas = await self.get_max_priority_fee_per_gas(block=last_block)

            base_fee = int(last_block['baseFeePerGas'] * 1.3)

            max_fee_per_gas = base_fee + max_priority_fee_per_gas

            tx = {
                'from': self.address,
                'chainId': await self.w3.eth.chain_id,
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas,
                'nonce': await self.w3.eth.get_transaction_count(self.address),
                'to': AsyncWeb3.to_checksum_address(
                    contract_address[module[8:] + '_address' \
                        if module.startswith('request') else module + '_address']),
                'value': value,
                'data': data
            }

            tx['gas'] = int(await self.w3.eth.estimate_gas(tx) * 1.3)

            sign = self.w3.eth.account.sign_transaction(tx, self.private_key)

            tx_hash = await self.w3.eth.send_raw_transaction(sign.rawTransaction)

            await check_transaction_status(tx_hash, self.w3, self.id)
        
        except Exception as er:
            logger.error(er)


    async def get_max_priority_fee_per_gas(self, block: dict) -> int:

        block_number = block['number']

        latest_block_transaction_count = await self.w3.eth.get_block_transaction_count(block_number)

        max_priority_fee_per_gas_list = []

        for _id in range(latest_block_transaction_count):
            try:
                transaction = await self.w3.eth.get_transaction_by_block(block_number, _id)

                if 'maxPriorityFeePerGas' in transaction:
                    max_priority_fee_per_gas_list.append(transaction['maxPriorityFeePerGas'])
            except:
                continue

        if not max_priority_fee_per_gas_list:
            max_priority_fee_per_gas = await self.w3.eth.max_priority_fee
        else:
            max_priority_fee_per_gas_list.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_list[len(max_priority_fee_per_gas_list) // 2]

        return max_priority_fee_per_gas
