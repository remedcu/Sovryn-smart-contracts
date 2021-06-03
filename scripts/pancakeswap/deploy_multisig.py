from brownie import *

import json

def main():
    loadConfig()

    balanceBefore = acct.balance()
    # Function Call
    deployMultisig()
    balanceAfter = acct.balance()

    print("=============================================================")
    print("ETH Before Balance:  ", balanceBefore)
    print("ETH After Balance:   ", balanceAfter)
    print("Gas Used:            ", balanceBefore - balanceAfter)
    print("=============================================================")

def loadConfig():
    global contracts, acct
    thisNetwork = network.show_active()

    # == Load config =======================================================================================================================
    if thisNetwork == "development":
        acct = accounts[0]
        configFile =  open('./scripts/pancakeswap/eth_testnet_contracts.json')
    elif thisNetwork == "rinkeby":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/pancakeswap/eth_testnet_contracts.json')
    elif thisNetwork == "mainnet":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/pancakeswap/eth_mainnet_contracts.json')
    else:
        raise Exception("network not supported")

    # Load deployed contracts addresses
    contracts = json.load(configFile)

# == Multisig Deployment ======================================
def deployMultisig():
    multisigOwner1, multisigOwner2, multisigOwner3 = contracts["multisigOwner1"], contracts["multisigOwner2"], contracts["multisigOwner3"]
    owners = [multisigOwner1, multisigOwner2, multisigOwner3]
    requiredConf = 1
    if network.show_active() == "mainnet":
        requiredConf = 2
    print("=============================================================")
    print("Deployment Parameters")
    print("=============================================================")
    print("Multisig Owners:         ", owners)
    print("Required Confirmations:  ", requiredConf)
    print("=============================================================")

    multisig = acct.deploy(MultiSigWallet, owners, requiredConf)
    print("=============================================================")
    print("Deployed Details")
    print("=============================================================")
    print("Multisig Address:        ", multisig)
    print("=============================================================")