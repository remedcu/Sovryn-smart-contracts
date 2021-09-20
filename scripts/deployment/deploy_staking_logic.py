from brownie import *

import time
import json
import csv
import math

def main():
    thisNetwork = network.show_active()

    # == Load config =======================================================================================================================
    if thisNetwork == "development":
        acct = accounts[0]
        configFile =  open('./scripts/contractInteraction/testnet_contracts.json')
    elif thisNetwork == "testnet":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/contractInteraction/testnet_contracts.json')
    elif thisNetwork == "rsk-mainnet":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/contractInteraction/mainnet_contracts.json')
    else:
        raise Exception("network not supported")

    contracts = json.load(configFile)

    print('deploying account:', acct)

    #deploy the staking logic contracts
    stakingLogic = acct.deploy(StakingTN)

    print("new staking logic address:", stakingLogic.address)
    print('''
    next steps: 
    STEP 1: SIP
     - create governance SIP to execute staking proxy 
       staking.setImplementation(newStakingLogic.address)
     - vote on SIP
     - in 3 days after SIP executed (in 3 days ater voting) run deploy_orig_claiming ")

    STEP 2: DEPLOY ORIG CLAIMING
    - deploy_orig_claiming will deploy VestingRegistry2 contract (without exchangeAllCSOV to prevent backdoor 
      double claiming by VestingRegistry users) and OriginInvestorsClaim contract bound to the VestingRegistry2 
      implementation.
    
    STEP 3: FUND CLAIMING
    - transfer total SOV amount to distribute to the origin investors to the OriginInvestorsClaim address
    
    STEP 4: LOAD REGISTRY
    - load the registry investor -> amount: run OriginInvestorsClaim.appendInvestorsAmountsList() by chunks of 
      250 records a time until all the list. 
      Make sure that OriginInvestorsClaim.totalAmount() == SOV.balanceOf(OriginInvestorsClaim)
    
    STEP 5: run OriginInvestorsClaim.setInvestorsAmountsListInitialized() to let the contract know that 
    it can execute the liated investors claim
    ''')

