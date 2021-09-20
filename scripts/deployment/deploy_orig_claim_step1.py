from brownie import *

import time
import json
import csv
import math


def main():
    thisNetwork = network.show_active()

    if thisNetwork == "development":
        acct = accounts[0]
        configFile = open(
            './scripts/contractInteraction/testnet_contracts.json')
    elif thisNetwork == "testnet":
        acct = accounts.load("rskdeployer")
        configFile = open(
            './scripts/contractInteraction/testnet_contracts.json')
    elif thisNetwork == "rsk-mainnet":
        acct = accounts.load("rskdeployer")
        configFile = open(
            './scripts/contractInteraction/mainnet_contracts.json')
    else:
        raise Exception("network not supported")

    # TODO check CSOV addresses in config files
    # load deployed contracts addresses
    contracts = json.load(configFile)
    multisig = contracts['multisig']
    teamVestingOwner = multisig

    print('deploying account:', acct)

    vestingLogic = acct.deploy(VestingLogic)
    vestingFactory = acct.deploy(VestingFactory, vestingLogic.address)

    if thisNetwork == "rsk-mainnet":
        feeSharingProxy = contracts["FeeSharingProxy"]
    else:
        staking = Contract.from_abi(
            "StakingTN", address=contracts['StakingTN'], abi=StakingTN.abi, owner=acct)
        feeSharingProxy = staking.feeSharing()

    PRICE_SATS = 2500
    vestingRegistry = acct.deploy(VestingRegistry2, vestingFactory.address, contracts["SOV"], [
                                  contracts["CSOV1"], contracts["CSOV2"]], PRICE_SATS, contracts["StakingTN"], feeSharingProxy, teamVestingOwner)
    vestingFactory.transferOwnership(vestingRegistry.address)

    claimContract = acct.deploy(OriginInvestorsClaim, vestingRegistry.address)
    vestingRegistry.addAdmin(claimContract.address)

    # can be done after deploy_orig_claim_step3.py
    # if thisNetwork == "rsk-mainnet":
    #     claimContract.transferOwnership(multisig)

    print(
        '''
        Next steps:
        1. Set OriginInvestorsClaim and VestingRegistry2 addresses in the relevant config: testnet_contracts.js or mainnet_contracts.js
        2. Run deploy_orig_claim_step2.py to load investors list by chunks of 250 records
        3. Fund OriginInvestorsClaim with SOV = 9073250102711580000000 (DECIMALS == 18). Should equal to OriginInvestorsClaim.totalAmount()
        4. Run deploy_orig_claim_step3.py to notify the claim contract that users can claim their SOV
        5. Notify origin investors that they can claim their tokens with the cliff == duration == Mar 26 2021
        '''
    )
