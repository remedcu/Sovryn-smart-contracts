from brownie import *
from brownie.network.contract import InterfaceContainer
import json
import time;
import copy

def main():
    
    #load the contracts and acct depending on the network
    loadConfig()

    totalVotingPower()

def loadConfig():
    global contracts, acct, values
    this_network = network.show_active()
    if this_network == "rsk-mainnet":
        configFile =  open('./scripts/contractInteraction/mainnet_contracts.json')
    elif this_network == "rsk-testnet":
        configFile =  open('./scripts/contractInteraction/testnet_contracts.json')
    contracts = json.load(configFile)
    acct = accounts.load("rskdeployer")

def totalVotingPower():

    staking = Contract.from_abi("StakingTN", address=contracts['StakingTN'], abi=StakingTN.abi, owner=acct)
    #len(chain) returns latest block + 1
    lastBlock = len(chain) - 2
    votingPower = staking.getPriorTotalVotingPower(lastBlock, time.time())
    print(votingPower/1e18)

