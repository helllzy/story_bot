from modules.account import CustomAccount
from modules.utils import sleeping, info
from data.data import KEYS, HELZY
from config import (
    MODULES,
    MODULES_COUNT,
    WALLETS_SLEEP,
    MODULES_SLEEP
)

from random import (
    randint,
    shuffle,
    sample,
    choice
)

from termcolor import cprint


def main(keys):

    for id, private_key in enumerate(keys, start=1):

        ALL_MODULES = sample(MODULES, randint(*MODULES_COUNT))

        account = CustomAccount(private_key)

        info(f'Working on {id} wallet: {account.address}')

        info(f'Actual modules: {", ".join(ALL_MODULES)}')

        for mod_id, module in enumerate(ALL_MODULES, start=1):

            info(f'Starting {module} module', 'blue')

            account.send_transaction(module)

            if mod_id != len(ALL_MODULES):
                sleeping(MODULES_SLEEP, "| Sleeping between modules", "yellow")

        sleeping(WALLETS_SLEEP, "| Sleeping between wallets\n", "cyan")


if __name__ == '__main__':
    shuffle(KEYS)

    cprint(choice(HELZY), choice(['green', 'magenta', 'light_cyan']))

    main(KEYS)
