from config import USE_PROXY
from modules.utils import logger

from json import load


with open('data/wallets.txt') as file:
    KEYS = [i.strip() for i in file.readlines()]

if len(KEYS) < 1:
    logger.critical("You didn`t add wallets in wallets.txt!")
    exit()

WALLETS, PROXIES = {}, []

if USE_PROXY:
    with open('data/proxies.txt') as file:
        PROXIES = [x.strip() for x in file.readlines()]

    if len(KEYS) > len(PROXIES):
        logger.critical('Number of wallets isn`t equal to number of proxies')
        exit()

for _id in range(len(KEYS)):

    WALLETS[f'w{_id}'] = {"private_key": KEYS[_id]}

    if USE_PROXY:
        WALLETS[f'w{_id}']["proxy"] = PROXIES[_id]

with open('data/abi/erc20_abi.json') as file:
    ERC20_ABI = load(file)

with open('data/abi/unleash_abi.json') as file:
    UNLEASH_ABI = load(file)

with open('data/abi/piperx_abi.json') as file:
    PIPERX_ABI = load(file)

contract_addresses = {
    'color_address': 0x59a0B4E4074B2DB51B218A7cAb3B4F4715C8b360,
    'nerzoNFT_story_address': 0x4e4e28211A7C533a0a1bF13fB80600ab48Ddb12a,
    'nerzoNFT_highway_address': 0x137b0Dbfb1Eb06eaB2c2706093aEEa936ADb6fbe,
    'nerzoNFT_storylliad_address': 0xf9789643c298c9D7F9d563Fd4b9DE6a25Ef46957,
    'morkieNFT_mystory_address': 0xdFa85cAB70EB073773Bf802bB31a5f67bDAF7AE8,
    'morkieNFT_story_address': 0x1e8df415F9Ae5E60f56B4648129D46a4bCc72a37,
    'piperx_address': '0x56300f2dB653393e78C7b5edE9c8f74237B76F47',
    'unleash_address': '0xB4a7Ea1f7874D0C55f19CB6a37aeB3F41a910276',
    'WBTC_address': '0x153B112138C6dE2CAD16D66B4B6448B7b88CAEF3',
    'USDC_address': '0x700722D24f9256Be288f56449E8AB1D27C4a70ca',
    'USDT_address': '0x8812d810EA7CC4e1c3FB45cef19D6a7ECBf2D85D',
    'WETH_address': '0x968B9a5603ddEb2A78Aa08182BC44Ece1D9E5bf0',
}

HELZY = [
'''
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |  ____  ____  | || |  _________   | || |   _____      | || |   ________   | || |  ____  ____  | |
| | |_   ||   _| | || | |_   ___  |  | || |  |_   _|     | || |  |  __   _|  | || | |_  _||_  _| | |
| |   | |__| |   | || |   | |_  \_|  | || |    | |       | || |  |_/  / /    | || |   \ \  / /   | |
| |   |  __  |   | || |   |  _|  _   | || |    | |   _   | || |     .'.' _   | || |    \ \/ /    | |
| |  _| |  | |_  | || |  _| |___/ |  | || |   _| |__/ |  | || |   _/ /__/ |  | || |    _|  |_    | |
| | |____||____| | || | |_________|  | || |  |________|  | || |  |________|  | || |   |______|   | |
| |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
''',
'''
 █████   █████ ██████████ █████       ███████████ █████ █████
░░███   ░░███ ░░███░░░░░█░░███       ░█░░░░░░███ ░░███ ░░███ 
 ░███    ░███  ░███  █ ░  ░███       ░     ███░   ░░███ ███  
 ░███████████  ░██████    ░███            ███      ░░█████   
 ░███░░░░░███  ░███░░█    ░███           ███        ░░███    
 ░███    ░███  ░███ ░   █ ░███      █  ████     █    ░███    
 █████   █████ ██████████ ███████████ ███████████    █████   
░░░░░   ░░░░░ ░░░░░░░░░░ ░░░░░░░░░░░ ░░░░░░░░░░░    ░░░░░    
''',
]
