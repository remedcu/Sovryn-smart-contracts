
'''
This script serves the purpose of interacting with existing smart contracts on the testnet or mainnet.
'''

from brownie import *
from brownie.network.contract import InterfaceContainer
import json
import time;
import copy
from scripts.utils import * 
import scripts.contractInteraction.config as conf
from scripts.contractInteraction.loan_tokens import *
from scripts.contractInteraction.protocol import *
from scripts.contractInteraction.staking_vesting import *
from scripts.contractInteraction.multisig import *
from scripts.contractInteraction.governance import *
from scripts.contractInteraction.liquidity_mining import *
from scripts.contractInteraction.amm import *
from scripts.contractInteraction.token import *
from scripts.contractInteraction.ownership import *
from scripts.contractInteraction.misc import *
from scripts.contractInteraction.prices import *

def main():
    
    #load the contracts and acct depending on the network
    conf.loadConfig()

    def stakeTokens(sovAmount, stakeTime, acctAddress, delegateeAddress):
        SOVtoken = Contract.from_abi("SOV", address=conf.contracts['SOV'], abi=SOV.abi, owner=acctAddress)
        staking = Contract.from_abi("StakingTN", address=conf.contracts['StakingProxyTN'], abi=StakingTN.abi, owner=acctAddress)

        until = int(time.time()) + int(stakeTime)
        amount = int(sovAmount) * (10 ** 18)

        SOVtoken.approve(staking.address, amount)
        tx = staking.stake(amount, until, acctAddress, delegateeAddress)

    def getDetails(acctAddress):
        staking = Contract.from_abi("StakingTN", address=conf.contracts['StakingProxyTN'], abi=StakingTN.abi, owner=acctAddress)
        #print(staking.kickoffTS())
        #print(staking.getStakes(acctAddress))
        #print(int(len(chain) - 2 - (((time.time()- 1632148108)/32))));
        #print(int(len(chain) - 2 - (((time.time()- 1632148108)/32))))
        #print(staking.getPriorWeightedStake(acctAddress, int(len(chain) - 2 - (((time.time()- 1632148108)/33))), 1632148108))
        #print(staking.getPriorWeightedStake(acctAddress, int(len(chain) - 2 - (((time.time()- 1632234508)/33))), 1632234508))
        #print(staking.getPriorWeightedStake(acctAddress, len(chain) - 2, 1632320908))
        #tx = staking.extendStakingDuration(1634351308, 1634437708, {"allow_revert": True})
        tx = staking.withdraw(1000000000000000000000, 1634437708, acctAddress)

    def getRewards(acctAddress):
        stakingRewards = Contract.from_abi("StakingRewardsTN", address=conf.contracts['StakingRewardsProxyTN'], abi=StakingRewardsTN.abi, owner=acctAddress)
        print(stakingRewards.getClaimableReward(False, {'from': acctAddress}))
        #print(stakingRewards.deploymentBlock())
        #print(stakingRewards.startTime())
        #print(stakingRewards.upgradeTime())
        print(stakingRewards.accumulatedRewards(acctAddress))
        a = stakingRewards.getClaimableReward(False, {'from': acctAddress})
        b = stakingRewards.accumulatedRewards(acctAddress)
        print(a-b)
        print(stakingRewards.withdrawals(acctAddress))
        print(stakingRewards.stakingActivity(acctAddress))

    def getImplementation():        
        # Get the proxy contract instance
        stakingProxy = Contract.from_abi("StakingProxyTN", address=conf.contracts['StakingProxyTN'], abi=StakingProxyTN.abi, owner=conf.acct)

        # Register logic in Proxy
        data = stakingProxy.getImplementation()
        print(data)

        #data = stakingProxy.getOwner()
        #print(data)

    #call the functions you want here
    #stakeTokens("1000", "2246400", "0x511893483DCc1A9A98f153ec8298b63BE010A99f", "0x511893483DCc1A9A98f153ec8298b63BE010A99f")
    #stakeTokens(1000, 4492800, "0x511893483DCc1A9A98f153ec8298b63BE010A99f", "0x511893483DCc1A9A98f153ec8298b63BE010A99f")
    #stakeTokens(1000, 6739200, "0x511893483DCc1A9A98f153ec8298b63BE010A99f", "0x511893483DCc1A9A98f153ec8298b63BE010A99f")
    #readStakingKickOff()
    #getDetails("0x511893483DCc1A9A98f153ec8298b63BE010A99f")
    getRewards("0x511893483DCc1A9A98f153ec8298b63BE010A99f")
    getRewards("0x9E0816a71B53ca67201a5088df960fE90910DE55")
    #getImplementation()

    #Bundle Deployment
    #upgradeStaking()
    #deployFeeSharingProxy()
    #deployConversionFeeSharingToWRBTC()
    #upgradeStakingRewards()
    #updateAddresses()

    #kickOff: Monday, 20 September 2021 19:58:28 - 1632148108
    #Upgrade: Wednesday, 22 September 2021 19:50:08 - 1632320408
    #deploymentBlock: 2189871
    #startTime: 1632148108