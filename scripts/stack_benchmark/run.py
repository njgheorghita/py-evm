#!/usr/bin/env python

import json
from pathlib import Path

from eth_utils import (
    encode_hex,
    decode_hex,
    to_canonical_address,
)
from ethpm import Package
from web3 import Web3

from eth.constants import (
    CREATE_CONTRACT_ADDRESS
)

from scripts.benchmark._utils.chain_plumbing import (
    FUNDED_ADDRESS,
    FUNDED_ADDRESS_PRIVATE_KEY,
    get_all_chains,
)
from scripts.benchmark._utils.tx import (
    new_transaction,
)


MANIFEST_PATH = Path(__file__).parent / 'package_manifests' / '1.0.0.json'
TEST_STACK_MANIFEST = json.loads(MANIFEST_PATH.read_text())
CONTRACT_NAME = 'TestStack'
W3_TX_DEFAULTS = {'gas': 0, 'gasPrice': 0}
FIRST_TX_GAS_LIMIT = 367724
SECOND_TX_GAS_LIMIT = 62050


def execute_TestStack_contract():
    w3 = Web3()
    
    # Create a Package for the TestStack manifest
    test_stack_pkg = Package(TEST_STACK_MANIFEST, w3)

    # Get the chains
    chains = tuple(get_all_chains())
    chain = chains[0]

    # Grab the contract factory to easily deploy new TestStack instances
    test_stack_contract_factory = test_stack_pkg.get_contract_factory("TestStack")

    # Build transaction to deploy the contract
    w3_tx1 = test_stack_contract_factory.constructor().buildTransaction(W3_TX_DEFAULTS)

    tx = new_transaction(
        vm=chain.get_vm(),
        private_key=FUNDED_ADDRESS_PRIVATE_KEY,
        from_=FUNDED_ADDRESS,
        to=CREATE_CONTRACT_ADDRESS,
        amount=0,
        gas=FIRST_TX_GAS_LIMIT,
        data=decode_hex(w3_tx1['data']),
    )

    block, receipt, computation = chain.apply_transaction(tx)
    deployed_contract_address = computation.msg.storage_address
    assert computation.is_success

    # Interact with the deployed contract by calling the totalSupply() API ?????

    # Grab the contract instance for the newly deployed TestStack
    test_stack_contract = test_stack_pkg.get_contract_instance(
        "TestStack",
        to_canonical_address(deployed_contract_address)
    ) 

    # Execute the computation
    w3_tx2 = test_stack_contract.functions.doLotsOfPops().buildTransaction(W3_TX_DEFAULTS)

    tx = new_transaction(
        vm=chain.get_vm(),
        private_key=FUNDED_ADDRESS_PRIVATE_KEY,
        from_=FUNDED_ADDRESS,
        to=deployed_contract_address,
        amount=0,
        gas=SECOND_TX_GAS_LIMIT,
        data=decode_hex(w3_tx2['data']),
    )

    block, receipt, computation = chain.apply_transaction(tx)
    # print(computation._memory._bytes)
    print(computation._stack.values)


def main():
    execute_TestStack_contract()


if __name__ == '__main__':
    main()
