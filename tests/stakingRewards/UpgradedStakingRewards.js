const { expect } = require("chai");
const { expectRevert, BN, constants, time } = require("@openzeppelin/test-helpers");

const { increaseTime, blockNumber } = require("../Utils/Ethereum");

const SOV_ABI = artifacts.require("SOV");
const StakingLogic = artifacts.require("StakingMockOld");
const StakingLogicNew = artifacts.require("StakingMock");
const StakingProxyTN = artifacts.require("StakingProxyTN");
const StakingRewardsTN = artifacts.require("StakingRewardsMockUpOld");
const StakingRewardsNew = artifacts.require("StakingRewardsMockUp");
const StakingRewardsProxyTN = artifacts.require("StakingRewardsProxyTN");
const FeeSharingLogic = artifacts.require("FeeSharingLogic");
const FeeSharingProxy = artifacts.require("FeeSharingProxy");
const Protocol = artifacts.require("sovrynProtocol");
const BlockMockUp = artifacts.require("BlockMockUp");
//Upgradable Vesting Registry
const VestingRegistryLogic = artifacts.require("VestingRegistryLogic");
const VestingRegistryProxy = artifacts.require("VestingRegistryProxy");

const wei = web3.utils.toWei;

const TOTAL_SUPPLY = "10000000000000000000000000";
const TWO_WEEKS = 1209600;
const DELAY = TWO_WEEKS;

contract("StakingRewardsTN - Upgrade", (accounts) => {
	let root, a1, a2, a3;
	let SOV, staking;
	let kickoffTS, inOneYear, inTwoYears, inThreeYears;

	before(async () => {
		[root, a1, a2, a3, ...accounts] = accounts;
		SOV = await SOV_ABI.new(TOTAL_SUPPLY);

		//Protocol
		protocol = await Protocol.new();

		//BlockMockUp
		blockMockUp = await BlockMockUp.new();

		//Deployed StakingTN Functionality
		let stakingLogic = await StakingLogic.new(SOV.address);
		stakingObj = await StakingProxyTN.new(SOV.address);
		await stakingObj.setImplementation(stakingLogic.address);
		staking = await StakingLogic.at(stakingObj.address);

		//Upgradable Vesting Registry
		vestingRegistryLogic = await VestingRegistryLogic.new();
		vesting = await VestingRegistryProxy.new();
		await vesting.setImplementation(vestingRegistryLogic.address);
		vesting = await VestingRegistryLogic.at(vesting.address);
		await staking.setVestingRegistry(vesting.address);

		kickoffTS = await staking.kickoffTS.call();
		inOneWeek = kickoffTS.add(new BN(DELAY));
		inOneYear = kickoffTS.add(new BN(DELAY * 26));
		inTwoYears = kickoffTS.add(new BN(DELAY * 26 * 2));
		inThreeYears = kickoffTS.add(new BN(DELAY * 26 * 3));

		//Transferred SOVs to a1
		await SOV.transfer(a1, wei("10000", "ether"));
		await SOV.approve(staking.address, wei("10000", "ether"), { from: a1 });

		//Transferred SOVs to a2
		await SOV.transfer(a2, wei("50000", "ether"));
		await SOV.approve(staking.address, wei("50000", "ether"), { from: a2 });

		//Transferred SOVs to a3
		await SOV.transfer(a3, wei("10000", "ether"));
		await SOV.approve(staking.address, wei("10000", "ether"), { from: a3 });

		let latest = await blockNumber();
		let blockNum = new BN(latest).add(new BN(291242 / 30));
		await blockMockUp.setBlockNum(blockNum);
		await increaseTime(291242);
		await staking.stake(wei("10000", "ether"), inThreeYears, a3, a3, { from: a3 });

		//StakingTN Reward Program is deployed
		let stakingRewardsLogic = await StakingRewardsTN.new();
		stakingRewardsObj = await StakingRewardsProxyTN.new();
		await stakingRewardsObj.setImplementation(stakingRewardsLogic.address);
		stakingRewards = await StakingRewardsTN.at(stakingRewardsObj.address);
		await stakingRewards.setBlockMockUpAddr(blockMockUp.address);
		await staking.setBlockMockUpAddr(blockMockUp.address);
	});

	describe("Flow - StakingRewardsTN", () => {
		it("should revert if SOV Address is invalid", async () => {
			await expectRevert(stakingRewards.initialize(constants.ZERO_ADDRESS, staking.address), "Invalid SOV Address.");
			//StakingTN Rewards Contract is loaded
			await SOV.transfer(stakingRewards.address, wei("1000000", "ether"));
			//Initialize
			await stakingRewards.initialize(SOV.address, staking.address); //Test - 24/08/2021
			await increaseTimeAndBlocks(100800);
			await staking.stake(wei("1000", "ether"), inOneYear, a1, a1, { from: a1 }); //StakingTN after program is initialised
			await increaseTimeAndBlocks(100800);
			await staking.stake(wei("50000", "ether"), inTwoYears, a2, a2, { from: a2 });
		});

		it("should account for stakes made till start date of the program for a1", async () => {			
			let numOfIntervals = 2;
			let totalAmount = 0;
			let fullTermAvg;
			let expectedAmount;

			fullTermAvg = avgWeight(37, 39, 9, 78);
			expectedAmount = numOfIntervals * ((1000 * fullTermAvg) / 26);
			totalAmount = totalAmount + expectedAmount;
			console.log(new BN(Math.floor(expectedAmount * 10 ** 10)).toString());

			fullTermAvg = avgWeight(41, 43, 9, 78);
			expectedAmount = numOfIntervals * ((5000 * fullTermAvg) / 26);
			totalAmount = totalAmount + expectedAmount;
			console.log(new BN(Math.floor(expectedAmount * 10 ** 10)).toString());

			fullTermAvg = avgWeight(63, 65, 9, 78);
			expectedAmount = numOfIntervals * ((3000 * fullTermAvg) / 26);
			totalAmount = totalAmount + expectedAmount;
			console.log(new BN(Math.floor(expectedAmount * 10 ** 10)).toString());

			fullTermAvg = avgWeight(66, 68, 9, 78);
			expectedAmount = numOfIntervals * ((1000 * fullTermAvg) / 26);
			totalAmount = totalAmount + expectedAmount;
			console.log(new BN(Math.floor(expectedAmount * 10 ** 10)).toString());
			console.log(new BN(Math.floor(totalAmount * 10 ** 10)).toString());

			//Ororo
			numOfIntervals = 15;
			fullTermAvg = avgWeight(27, 42, 9, 78);
			expectedAmt = numOfIntervals * ((1000 * fullTermAvg) / 26);
			let total = 0;
			total = total + expectedAmt;
			console.log(new BN(Math.floor(expectedAmt * 10 ** 10)).toString());

			fullTermAvg = avgWeight(63, 78, 9, 78);
			expectedAmt = numOfIntervals * ((1000 * fullTermAvg) / 26);
			total = total + expectedAmt;
			console.log(new BN(Math.floor(expectedAmt * 10 ** 10)).toString());
			console.log(new BN(Math.floor(total * 10 ** 10)).toString());
		});
	});

	function avgWeight(from, to, maxWeight, maxDuration) {
		let weight = 0;
		for (let i = from; i < to; i++) {
			weight += Math.floor(((maxWeight * (maxDuration ** 2 - (maxDuration - i) ** 2)) / maxDuration ** 2 + 1) * 10, 2);
		}
		weight /= to - from;
		return (weight / 100) * 0.2975;
	}

	async function increaseTimeAndBlocks(seconds) {
		let latest = await blockMockUp.getBlockNum();
		let blockNum = new BN(latest).add(new BN(seconds / 30));
		await blockMockUp.setBlockNum(blockNum);
		await increaseTime(seconds);
	}
});
