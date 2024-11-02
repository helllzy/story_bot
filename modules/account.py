from modules.utils import check_gas, check_transaction_status, logger, sleeping
from data.data import contract_addresses, USE_PROXY, ERC20_ABI, UNLEASH_ABI, PIPERX_ABI
from config import RPC

from random import randint, shuffle, choice, uniform
from time import time

from web3 import AsyncWeb3
from web3.middleware import async_geth_poa_middleware


class CustomAccount():
    def __init__(self, wallet: str, id: int, request_kwargs: dict = {}):
        self.tokens_for_liquidity = ['WBTC', 'USDC', 'USDT', 'WETH']
        self.routes = {
            contract_addresses['WBTC_address']: [contract_addresses['USDT_address'], contract_addresses['USDC_address']],
            contract_addresses['WETH_address']: [contract_addresses['USDT_address'], contract_addresses['USDC_address']],
            contract_addresses['USDT_address']: [contract_addresses['WBTC_address'], contract_addresses['WETH_address'], contract_addresses['USDC_address']],
            contract_addresses['USDC_address']: [contract_addresses['WBTC_address'], contract_addresses['WETH_address'], contract_addresses['USDT_address']]
        }
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


    async def get_max_priority_fee(self):
        last_block = await self.w3.eth.get_block('latest')

        max_priority_fee_per_gas = await self.get_max_priority_fee_per_gas(block=last_block)

        base_fee = int(last_block['baseFeePerGas'] * 1.3)

        max_fee_per_gas = base_fee + max_priority_fee_per_gas

        return max_fee_per_gas, max_priority_fee_per_gas


    async def approve(self, token_address, approval_address, amount):
        approve_contract = self.w3.eth.contract(token_address, abi=ERC20_ABI)

        tx_data = await self.get_tx_data()

        tx = await approve_contract.functions.approve(
            to=approval_address,
            tokenId=amount
            ).build_transaction(tx_data)
        
        return tx


    async def supply(self, contract_address, token_for_supply, amount):
        supply_contract = self.w3.eth.contract(contract_address, abi=UNLEASH_ABI)

        tx_data = await self.get_tx_data()

        tx = await supply_contract.functions.supply(
            arg0=token_for_supply,
            arg1=amount,
            arg2=self.address,
            arg3=0,
            ).build_transaction(tx_data)
        
        return tx


    async def borrow(self, contract_address, supplied_token):
        try:
            token_for_borrow = choice(self.routes[supplied_token])

            if token_for_borrow == contract_addresses['WETH_address']:
                amount = int(uniform(0.01, 0.3)*1e18)
            elif token_for_borrow == contract_addresses['WBTC_address']:
                amount = int(uniform(0.01, 0.3)*1e8)
            else:
                amount = int(randint(50, 500)*1e6)

            borrow_contract = self.w3.eth.contract(contract_address, abi=UNLEASH_ABI)
            
            tx_data = await self.get_tx_data()

            tx = await borrow_contract.functions.borrow(
                arg0=token_for_borrow,
                arg1=amount,
                arg2=2,
                arg3=0,
                arg4=self.address
                ).build_transaction(tx_data)
            
            return tx
        except Exception as er:
            print(er)


    async def swap(self, contract_address, from_token, balance):

        to_token = choice(self.routes[from_token])

        tx_data = await self.get_tx_data()

        path = [from_token, to_token]

        contract = self.w3.eth.contract(contract_address, abi=PIPERX_ABI)

        min_amount_out = await contract.functions.getAmountsOut(amountIn=balance, path=path).call()

        tx = await contract.functions.swapExactTokensForTokens(
            amountIn=min_amount_out[0],
            amountOutMin=int(min_amount_out[1]*0.98),
            path=path,
            to=self.address,
            deadline=int(time()) + 100
        ).build_transaction(tx_data)

        return tx


    async def get_tx_data(self):

        max_fee_per_gas, max_priority_fee_per_gas = await self.get_max_priority_fee()

        tx_data = {
            "chainId": await self.w3.eth.chain_id,
            "from": self.address,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
        }

        return tx_data


    async def check_balance(self):
        tokens = self.tokens_for_liquidity
        shuffle(tokens)

        for token in tokens:
            checksum_address = contract_addresses[f'{token}_address']
            contract = self.w3.eth.contract(
                address=checksum_address,
                abi=ERC20_ABI
                )

            balance = await contract.functions.balanceOf(self.address).call()

            if balance > 0:
                return checksum_address, balance
        
        return False, False


    async def module_processing(self, module: str, second_module=None):
        for _ in range(2):
            if module in ['unleash_supply', 'piperx_swap']:
                token_address, balance = await self.check_balance()

                if token_address:
                    tx_data = await self.approve(token_address, contract_addresses[module[:module.find('_')]+'_address'], balance)
                    await self.send_transaction(tx_data)
                    await sleeping([3, 5], f'[{self.id}] | Sleeping after approval', 'yellow')

                    if module == 'unleash_supply':
                        tx_data = await self.supply(contract_addresses['unleash_address'], token_address, balance)
                        await self.send_transaction(tx_data)
                        await sleeping([3, 5], f'[{self.id}] | Sleeping after supplying', 'yellow')
                        tx_data = await self.borrow(contract_addresses['unleash_address'], token_address)
                    elif module == 'piperx_swap':
                        tx_data = await self.swap(contract_addresses['piperx_address'], token_address, balance)

                    return await self.send_transaction(tx_data)
                else:
                    logger.debug(f'[{self.id}] | Doesn`t have any tokens, going to request tokens')
                    second_module = module
                    module = f'request_{choice(self.tokens_for_liquidity)}'

            data, value = await self.get_transaction_data(module)

            tx_data = await self.get_tx_data()

            tx_data.update(
                {
                    "to": AsyncWeb3.to_checksum_address(
                        contract_addresses[module[8:] + '_address' \
                        if module.startswith('request') else module + '_address']),
                    "data": data
                }
            )

            if type(second_module) == str:
                module = second_module
                await self.send_transaction(tx_data)
                await sleeping([3, 5], f'[{self.id}] | Sleeping before {module}', 'yellow')
            else:
                return await self.send_transaction(tx_data)


    async def get_transaction_data(self, module: str, value: float = 0):

        if module.startswith('request'):
            data = '0x9f678cca'

        elif 'NFT' in module:
            data = '0x84bb1e42' + '0' * (64-len(str(self.address)[2:])) + str(self.address)[2:] + '0' * 63
            quantity = randint(1, 3)
            try:
                match module:
                    case 'nerzoNFT_story':
                        data += str(quantity) + '0' * 24 + 'e' * 40 + '0' * 126 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                            '0' * 64 + 'a' + '0' * 88 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                    case 'nerzoNFT_highway':
                        data += str(quantity) + '0' * 24 + 'e' * 40 + '0' * 126 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                            '0' + 'f' * 64 + '0' * 88 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                    case 'nerzoNFT_storylliad':
                        data = str(quantity) + '0' * 24 + 'e' * 40 + '0' * 49 + '0b1a2bc2ec5' + '0' * 66 + 'c' + '0' * 62 + '18' + '0' * 63 + '80' + \
                            'f' * 64 + '0' * 49 + '0b1a2bc2ec5' + '0' * 28 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                        value = 1 * 0.05
                    case 'morkieNFT_mystory':
                        data += '1' + '0' * 24 + 'e' * 40 + '0' * 49 + '0b1a2bc2ec5' + '0' * 66 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                            '0' * 64 + '1' + '0' * 49 + '0b1a2bc2ec5' + '0' * 28 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                        value = 0.05
                    case 'morkieNFT_story':
                        data += '1' + '0' * 24 + 'e' * 40 + '0' * 49 + '16345785d8a' + '0' * 66 + 'c' + '0' * 62 + '18' + '0' * 63 + '8' + \
                            '0' * 64 + '1' + '0' * 49 + '16345785d8a' + '0' * 28 + 'e' * 40 + '0' * 63 + '1' + '0' * 128
                        value = 0.1
            except Exception as er:
                print(er)
        else:
            match module:
                case 'color':
                    data = '0x40d097c3' + '0' * (64-len(str(self.address)[2:])) + str(self.address)[2:]

        return data, int(value*1e18)


    @check_gas
    async def send_transaction(self, tx_data: dict):
        try:
            tx_data['gas'] = int(await self.w3.eth.estimate_gas(tx_data) * 1.3)

            sign = self.w3.eth.account.sign_transaction(tx_data, self.private_key)

            tx_hash = await self.w3.eth.send_raw_transaction(sign.rawTransaction)

            await check_transaction_status(tx_hash, self.w3, self.id)
        except Exception as er:
            print(er)


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
