'''
-----------------|available modules|-----------------|
"color"                                              |
"nerzoNFT_story"                                     |
"nerzoNFT_highway"                                   |
"unleash_supply"                                     |
"piperx_swap"                                        |
"request_WBTC"                                       |
"request_USDC"                                       |
"request_USDT"                                       |
"request_WETH"                                       |
-----------|these modules are not working|-----------|
"morkieNFT_mystory"                                  |
"morkieNFT_story"                                    |
"nerzoNFT_storylliad"                                |
-----------------------------------------------------|
'''

MODULES = [
"color",
"nerzoNFT_story",
"nerzoNFT_highway",
"request_WBTC",
"request_USDC",
"request_USDT",
"request_WETH",
"unleash_supply",
"piperx_swap"
]

MODULES_COUNT = [5, 9]

WALLETS_SLEEP = [50, 200]
MODULES_SLEEP = [5, 30]

RPC = 'https://testnet.storyrpc.io'

MAX_GWEI = 50

USE_PROXY = True

THREADS_COUNT = 1
