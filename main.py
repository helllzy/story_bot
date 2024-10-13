from sys import platform
from time import sleep
from asyncio import WindowsSelectorEventLoopPolicy, set_event_loop_policy, run
from modules.account import CustomAccount
from modules.utils import sleeping, info
from data.data import WALLETS, HELZY
from config import (
    MODULES,
    MODULES_COUNT,
    WALLETS_SLEEP,
    MODULES_SLEEP,
    THREADS_COUNT
)

from random import (
    randint,
    shuffle,
    sample,
    choice
)

from concurrent.futures import ThreadPoolExecutor
from termcolor import cprint


async def proceed_wallet(wallet, id):

    ALL_MODULES = sample(MODULES, randint(*MODULES_COUNT))

    account = CustomAccount(WALLETS[wallet], id)

    await info(f'[{id}] | {account.address} | Actual modules: {", ".join(ALL_MODULES)}')

    for mod_id, module in enumerate(ALL_MODULES, start=1):

        await info(f'[{id}] | Starting {module} module', 'blue')

        await account.send_transaction(module)

        if mod_id != len(ALL_MODULES):
            await sleeping(MODULES_SLEEP, f"[{id}] | Sleeping between modules", "yellow")


def run_wallet(wallet, id):
    run(proceed_wallet(wallet, id))


def main():

    with ThreadPoolExecutor(max_workers=THREADS_COUNT) as executor:

        for id, wallet in enumerate(wallets, start=1):
            executor.submit(
                run_wallet,
                wallet,
                id
            )

            sleep(randint(*WALLETS_SLEEP))


if __name__ == '__main__':

    wallets = list(WALLETS.keys())

    shuffle(wallets)

    cprint(choice(HELZY), choice(['green', 'magenta', 'light_cyan']))

    if platform.startswith("win"):
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    main()
