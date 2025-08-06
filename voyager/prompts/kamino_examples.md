# Kamino SDK Examples Reference

Complete examples from the Kamino Finance SDK repository for use in Solana Gym exploration.

## Core Constants

```typescript
// Main Kamino market on mainnet
const MAIN_MARKET = new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF');
const PROGRAM_ID = new PublicKey('KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD');

// Common token mints
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
const SOL_MINT = new PublicKey('So11111111111111111111111111111111111111112');
const PYUSD_MINT = new PublicKey('2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo');
```

## 1. Deposit Example

```typescript
import { KaminoAction, VanillaObligation } from '@kamino-finance/klend-sdk';
import { Connection, PublicKey, Keypair } from '@solana/web3.js';
import BN from 'bn.js';

export async function depositExample(blockhash: string): Promise<string> {
    const connection = new Connection('http://localhost:8899');
    const MAIN_MARKET = new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF');
    const PROGRAM_ID = new PublicKey('KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD');
    const wallet = Keypair.generate(); // Use test wallet
    
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    await market.loadReserves();
    
    const depositAction = await KaminoAction.buildDepositTxns(
        market,
        new BN(1_000_000), // 1 USDC (6 decimals)
        market.getReserve("USDC").getLiquidityMint(),
        wallet.publicKey,
        new VanillaObligation(PROGRAM_ID),
        false,           // includeUserMetadata
        undefined,       // tipTxBuilder
        300_000,        // priority fee
        true            // createObligationIxns
    );
    
    // Combine all instructions
    const tx = new Transaction();
    tx.add(...depositAction.computeBudgetIxs);
    tx.add(...depositAction.setupIxs);
    tx.add(...depositAction.lendingIxs);
    tx.add(...depositAction.cleanupIxs);
    
    tx.recentBlockhash = blockhash;
    tx.feePayer = wallet.publicKey;
    
    return tx.serialize().toString('base64');
}
```

## 2. Borrow Example

```typescript
import { KaminoAction, VanillaObligation } from '@kamino-finance/klend-sdk';

export async function borrowExample(blockhash: string): Promise<string> {
    const connection = new Connection('http://localhost:8899');
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    await market.loadReserves();
    
    // User needs collateral deposited first
    const borrowAction = await KaminoAction.buildBorrowTxns(
        market,
        new BN(1_000_000), // 1 USDC
        market.getReserve("USDC").getLiquidityMint(),
        wallet.publicKey,
        new VanillaObligation(PROGRAM_ID),
        true,              // includeUserMetadata
        undefined          // tipTxBuilder
    );
    
    const tx = new Transaction();
    tx.add(...borrowAction.computeBudgetIxs);
    tx.add(...borrowAction.setupIxs);
    tx.add(...borrowAction.lendingIxs);
    tx.add(...borrowAction.cleanupIxs);
    
    tx.recentBlockhash = blockhash;
    return tx.serialize().toString('base64');
}
```

## 3. Repay Example

```typescript
export async function repayExample(blockhash: string): Promise<string> {
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    await market.loadReserves();
    
    const repayAction = await KaminoAction.buildRepayTxns(
        market,
        new BN(500_000), // 0.5 USDC
        market.getReserve("USDC").getLiquidityMint(),
        wallet.publicKey,
        new VanillaObligation(PROGRAM_ID),
        true,              // includeUserMetadata
        undefined          // tipTxBuilder
    );
    
    const tx = new Transaction();
    tx.add(...repayAction.lendingIxs);
    tx.recentBlockhash = blockhash;
    return tx.serialize().toString('base64');
}
```

## 4. Withdraw Example

```typescript
export async function withdrawExample(blockhash: string): Promise<string> {
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    await market.loadReserves();
    
    const withdrawAction = await KaminoAction.buildWithdrawTxns(
        market,
        new BN(1_000_000), // 1 USDC
        market.getReserve("USDC").getLiquidityMint(),
        wallet.publicKey,
        new VanillaObligation(PROGRAM_ID),
        true,              // includeUserMetadata
        undefined          // tipTxBuilder
    );
    
    const tx = new Transaction();
    tx.add(...withdrawAction.lendingIxs);
    tx.recentBlockhash = blockhash;
    return tx.serialize().toString('base64');
}
```

## 5. Get User Obligations

```typescript
export async function getUserObligations(): Promise<void> {
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    const userWallet = new PublicKey("USER_WALLET_ADDRESS");
    
    // Get vanilla obligation
    const obligation = await market.getUserVanillaObligation(userWallet);
    console.log("User LTV:", obligation?.loanToValue());
    console.log("Health factor:", obligation?.healthFactor());
    
    // Get all obligations for a specific reserve
    const reserve = market.getReserve("SOL");
    const obligations = await market.getAllUserObligationsForReserve(
        userWallet, 
        reserve.address
    );
    
    // Check if reserve is in obligation
    const isInObligation = market.isReserveInObligation(obligation, reserve.address);
}
```

## 6. Query Obligations by Reserve

```typescript
export async function getObligationsByReserve(): Promise<void> {
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    const reserveAddress = new PublicKey("RESERVE_ADDRESS");
    
    // Get all obligations that have deposited this reserve
    const loans = await market.getAllObligationsByDepositedReserve(reserveAddress);
    
    let totalDeposits = new Decimal(0);
    for (const loan of loans) {
        const depositAmount = loan.getDepositByReserve(reserveAddress)?.amount;
        if (depositAmount) {
            totalDeposits = totalDeposits.plus(depositAmount);
            console.log('Obligation:', loan.obligationAddress.toString());
            console.log('Deposit amount:', depositAmount.toString());
        }
    }
}
```

## 7. Liquidation Example

```typescript
export async function liquidateExample(blockhash: string): Promise<string> {
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    await market.loadReserves();
    
    // Find an unhealthy obligation to liquidate
    const obligationToLiquidate = await market.getObligationByAddress(
        new PublicKey("OBLIGATION_ADDRESS")
    );
    
    const liquidateAction = await KaminoAction.buildLiquidateTxns(
        market,
        new BN(100_000),    // amount to liquidate
        "USDC",             // collateral symbol to receive
        "SOL",              // debt symbol to repay
        obligationToLiquidate,
        wallet.publicKey,
        new VanillaObligation(PROGRAM_ID)
    );
    
    const tx = new Transaction();
    tx.add(...liquidateAction.lendingIxs);
    tx.recentBlockhash = blockhash;
    return tx.serialize().toString('base64');
}
```

## 8. Harvest Rewards Example

```typescript
import { Farms } from '@kamino-finance/farms-sdk';

export async function harvestRewards(): Promise<string> {
    const farm = new Farms(connection);
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    const reserve = market.getReserve("PYUSD");
    
    // Get all farms user is eligible for rewards
    const txInstructions = await farm.claimForUserForFarmAllRewardsIx(
        wallet.publicKey, 
        reserve.state.farmCollateral, 
        true  // skipUnknownRewards
    );
    
    const tx = new Transaction();
    tx.add(...txInstructions);
    tx.recentBlockhash = blockhash;
    return tx.serialize().toString('base64');
}
```

## 9. Reserve APY and Stats

```typescript
export async function getReserveStats(): Promise<void> {
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    await market.loadReserves();
    
    const reserve = market.getReserve("USDC");
    
    // Get APY
    const supplyAPY = reserve.calculateSupplyAPY();
    const borrowAPY = reserve.calculateBorrowAPY();
    
    console.log("Supply APY:", supplyAPY.toString());
    console.log("Borrow APY:", borrowAPY.toString());
    
    // Get reserve stats
    console.log("Total deposits:", reserve.stats.totalDepositsWads.toString());
    console.log("Total borrows:", reserve.stats.totalBorrowsWads.toString());
    console.log("Utilization rate:", reserve.calculateUtilizationRatio().toString());
    
    // Get caps
    console.log("Deposit cap:", reserve.stats.depositCap?.toString());
    console.log("Borrow cap:", reserve.stats.borrowCap?.toString());
}
```

## 10. Complex Operations with Swaps

```typescript
import { getRepayWithCollSwapInputs } from '@kamino-finance/klend-sdk';

export async function repayWithCollateral(): Promise<void> {
    const market = await KaminoMarket.load(connection, MAIN_MARKET);
    const obligation = await market.getObligationByAddress(new PublicKey("OBL_ADDRESS"));
    
    const collTokenMint = USDC_MINT;
    const debtTokenMint = PYUSD_MINT;
    const debtReserve = market.getReserveByMint(debtTokenMint);
    
    const repayAmount = obligation?.borrows.get(debtReserve.address)?.amount || new Decimal(0);
    
    // Calculate swap inputs for repaying with collateral
    const estimatedStats = await getRepayWithCollSwapInputs(
        jupiterQuoter,  // Jupiter for swaps
        {
            obligation: obligation,
            repayTokenMint: debtTokenMint,
            repayAmount: repayAmount,
            collTokenMint: collTokenMint,
            maxSlippageBps: 100,  // 1% slippage
            currentSlot: new Decimal(currentSlot),
        },
        wallet
    );
    
    console.log("Collateral to sell:", estimatedStats.collAmountOut);
    console.log("Final LTV:", estimatedStats.ltvAfter);
    console.log("Health factor after:", estimatedStats.hfAfter);
}
```

## Available Example Files in SDK

The complete list of examples available in the Kamino SDK repository:

1. `example_borrow.ts` - Borrowing from lending pool
2. `example_burn_ctokens_redeem_tokens.ts` - Burning cTokens to redeem underlying
3. `example_change_market_admin.ts` - Admin operations
4. `example_deposit_in_obligation.ts` - Depositing collateral
5. `example_deposit_mint_ctokens.ts` - Minting cTokens
6. `example_get_obligations_based_on_reserve_filter.ts` - Querying obligations
7. `example_harvest_reward.ts` - Claiming farming rewards
8. `example_loan_info.ts` - Getting loan information
9. `example_loan_ltv.ts` - Calculating loan-to-value ratios
10. `example_loan_value.ts` - Calculating loan values
11. `example_market_reserves.ts` - Listing market reserves
12. `example_multiply_adjust_transaction.ts` - Leverage adjustments
13. `example_multiply_deposit_transaction.ts` - Leverage deposits
14. `example_multiply_withdraw_transaction.ts` - Leverage withdrawals
15. `example_obligation_order.ts` - Ordering obligations
16. `example_read_supplied_and_borrowed_token_and_pending_rewards_for_user.ts` - User positions
17. `example_repay_with_coll_calcs.ts` - Repaying with collateral
18. `example_reserve_apy.ts` - Reserve APY calculations
19. `example_reserve_apy_history.ts` - Historical APY data
20. `example_reserve_caps.ts` - Reserve deposit/borrow caps
21. `example_reserve_reward_apy.ts` - Reward APY calculations
22. `example_reserve_supply_and_borrow.ts` - Supply and borrow stats
23. `example_swap_coll_simulation.ts` - Simulating collateral swaps
24. `example_user_loans.ts` - User loan positions

## Important Notes

1. All examples use the main Kamino market at `7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF`
2. The program ID is `KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD`
3. Most operations require setup instructions (creating ATAs, refreshing reserves)
4. Always include compute budget instructions for complex operations
5. Use `VanillaObligation` for standard lending, other types for leverage/multiply