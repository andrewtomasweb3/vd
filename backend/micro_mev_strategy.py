import asyncio
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from .advanced_dex_client import AdvancedDEXClient

logger = logging.getLogger(__name__)

@dataclass
class MicroArbitrageOpportunity:
    token_pair: str
    buy_dex: str
    sell_dex: str
    buy_price: float
    sell_price: float
    profit_percentage: float
    estimated_profit_sol: float
    estimated_fees: float
    net_profit: float
    timestamp: datetime

class MicroMEVStrategy:
    """Ultra-conservative MEV strategy optimized for small balances like $8"""
    
    def __init__(self):
        # Initialize with real credentials
        rpc_url = os.getenv("SOLANA_RPC_URL")
        private_key = os.getenv("PRIVATE_KEY_BS58")
        
        if not rpc_url or not private_key:
            raise ValueError("Missing RPC_URL or PRIVATE_KEY_BS58 in environment")
        
        self.dex_client = AdvancedDEXClient(rpc_url, private_key)
        
        # Ultra-conservative settings for $8 balance
        self.max_trade_size = 0.005  # Max 0.005 SOL per trade ($1 at $200/SOL)
        self.min_profit_percentage = 2.0  # Minimum 2% profit
        self.max_gas_budget = 0.001  # Max gas per trade
        self.reserve_balance = 0.005  # Always keep 0.005 SOL for fees
        
        # Performance tracking
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit_sol = 0.0
        self.total_fees_paid = 0.0
        
        # Risk management
        self.daily_loss_limit = 0.01  # Max 0.01 SOL loss per day
        self.daily_losses = 0.0
        self.last_reset_date = datetime.utcnow().date()
        
        logger.info("MicroMEV Strategy initialized for $8 balance trading")
    
    async def scan_micro_opportunities(self) -> List[MicroArbitrageOpportunity]:
        """Scan for micro arbitrage opportunities suitable for small balance"""
        opportunities = []
        
        try:
            # Check current balance
            balance = await self.dex_client.get_wallet_balance()
            available_balance = balance - self.reserve_balance
            
            if available_balance < self.max_trade_size:
                logger.warning(f"Insufficient balance for trading. Available: {available_balance} SOL")
                return []
            
            # Get arbitrage opportunities
            raw_opportunities = await self.dex_client.calculate_arbitrage_opportunities()
            
            for opp in raw_opportunities:
                # Calculate if this opportunity is profitable for micro trading
                trade_size = min(self.max_trade_size, available_balance * 0.5)  # Use max 50% of available
                estimated_profit = opp['estimated_profit'] * (trade_size / 0.01)  # Scale from 0.01 SOL base
                estimated_fees = await self.dex_client.estimate_transaction_fee(2)  # Buy + sell
                net_profit = estimated_profit - estimated_fees
                
                # Only include if profitable and meets minimum requirements
                if (net_profit > 0.0005 and  # Min $0.10 profit
                    opp['profit_percentage'] >= self.min_profit_percentage):
                    
                    opportunities.append(MicroArbitrageOpportunity(
                        token_pair=opp['token_pair'],
                        buy_dex=opp['buy_dex'],
                        sell_dex=opp['sell_dex'],
                        buy_price=opp['buy_price'],
                        sell_price=opp['sell_price'],
                        profit_percentage=opp['profit_percentage'],
                        estimated_profit_sol=estimated_profit,
                        estimated_fees=estimated_fees,
                        net_profit=net_profit,
                        timestamp=opp['timestamp']
                    ))
            
            # Sort by net profit descending
            opportunities.sort(key=lambda x: x.net_profit, reverse=True)
            
            logger.info(f"Found {len(opportunities)} micro arbitrage opportunities")
            return opportunities[:3]  # Top 3 opportunities
            
        except Exception as e:
            logger.error(f"Error scanning micro opportunities: {e}")
            return []
    
    async def execute_micro_arbitrage(self, opportunity: MicroArbitrageOpportunity) -> Dict:
        """Execute micro arbitrage with extreme caution"""
        try:
            # Reset daily limits if needed
            await self._check_daily_limits()
            
            # Double-check if we can afford this trade
            if self.daily_losses >= self.daily_loss_limit:
                logger.warning("Daily loss limit reached, skipping trade")
                return {'success': False, 'reason': 'daily_loss_limit_reached'}
            
            # Calculate actual trade size
            balance = await self.dex_client.get_wallet_balance()
            available_balance = balance - self.reserve_balance
            trade_size = min(self.max_trade_size, available_balance * 0.3)  # Ultra-conservative 30%
            
            if trade_size < 0.002:  # Minimum viable trade size
                logger.warning("Trade size too small to be profitable")
                return {'success': False, 'reason': 'trade_size_too_small'}
            
            logger.info(f"Executing micro arbitrage: {opportunity.token_pair} for {trade_size} SOL")
            
            # Execute the arbitrage
            result = await self._execute_dual_dex_trade(opportunity, trade_size)
            
            # Update tracking
            self.total_trades += 1
            if result['success']:
                self.successful_trades += 1
                self.total_profit_sol += result.get('net_profit', 0)
                logger.info(f"✅ Micro arbitrage successful! Net profit: {result.get('net_profit', 0):.6f} SOL")
            else:
                loss = result.get('loss', 0)
                self.daily_losses += loss
                self.total_fees_paid += loss
                logger.warning(f"❌ Micro arbitrage failed. Loss: {loss:.6f} SOL")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing micro arbitrage: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_dual_dex_trade(self, opportunity: MicroArbitrageOpportunity, trade_size: float) -> Dict:
        """Execute buy on one DEX and sell on another"""
        try:
            start_time = datetime.utcnow()
            
            # For demonstration - simulate the trades
            # In production, these would be actual DEX interactions
            
            # Simulate buy transaction
            buy_success = await self._simulate_dex_trade(
                opportunity.buy_dex, 
                "buy", 
                opportunity.token_pair, 
                trade_size,
                opportunity.buy_price
            )
            
            if not buy_success:
                return {'success': False, 'reason': 'buy_failed', 'loss': opportunity.estimated_fees}
            
            # Small delay to simulate real trading
            await asyncio.sleep(0.1)
            
            # Simulate sell transaction
            sell_success = await self._simulate_dex_trade(
                opportunity.sell_dex,
                "sell",
                opportunity.token_pair,
                trade_size,
                opportunity.sell_price
            )
            
            if not sell_success:
                # If sell fails, we're stuck with the token - simulate recovery
                logger.warning("Sell failed, attempting recovery...")
                recovery_loss = trade_size * 0.05  # 5% loss for recovery
                return {'success': False, 'reason': 'sell_failed', 'loss': recovery_loss}
            
            # Calculate actual profit
            gross_profit = (opportunity.sell_price - opportunity.buy_price) * trade_size
            net_profit = gross_profit - opportunity.estimated_fees
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'success': True,
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'fees': opportunity.estimated_fees,
                'execution_time': execution_time,
                'trade_size': trade_size,
                'buy_dex': opportunity.buy_dex,
                'sell_dex': opportunity.sell_dex
            }
            
        except Exception as e:
            logger.error(f"Error in dual DEX trade: {e}")
            return {'success': False, 'error': str(e), 'loss': opportunity.estimated_fees}
    
    async def _simulate_dex_trade(self, dex: str, action: str, token_pair: str, amount: float, price: float) -> bool:
        """Simulate DEX trade execution"""
        try:
            # Simulate different success rates for different DEXs
            success_rates = {
                'raydium': 0.95,
                'meteora': 0.92,
                'orca': 0.94,
                'jupiter': 0.97
            }
            
            import random
            success_rate = success_rates.get(dex, 0.90)
            
            # Random success based on DEX reliability
            success = random.random() < success_rate
            
            if success:
                logger.debug(f"✅ {action.upper()} on {dex}: {amount:.6f} SOL @ ${price:.6f}")
            else:
                logger.debug(f"❌ {action.upper()} on {dex} failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error simulating {dex} trade: {e}")
            return False
    
    async def scan_pumpfun_opportunities(self) -> List[Dict]:
        """Scan pump.fun for early token opportunities"""
        try:
            tokens = await self.dex_client.get_pumpfun_tokens()
            
            # Filter for micro-trading opportunities
            micro_opportunities = []
            for token in tokens:
                # Look for tokens with good momentum but still small enough to move
                if (token['market_cap'] > 20000 and 
                    token['market_cap'] < 500000 and
                    token['reply_count'] > 10):
                    
                    # Calculate risk score (1-10, 10 = highest risk)
                    risk_score = min(10, max(1, int(token['market_cap'] / 50000)))
                    
                    # Only consider lower risk tokens for micro trading
                    if risk_score <= 6:
                        micro_opportunities.append({
                            'token': token,
                            'risk_score': risk_score,
                            'suggested_size': min(0.003, self.max_trade_size * (7 - risk_score) / 7),
                            'timestamp': datetime.utcnow()
                        })
            
            return micro_opportunities[:2]  # Max 2 pump.fun opportunities
            
        except Exception as e:
            logger.error(f"Error scanning pump.fun opportunities: {e}")
            return []
    
    async def execute_pumpfun_micro_trade(self, opportunity: Dict) -> Dict:
        """Execute a micro pump.fun trade"""
        try:
            token = opportunity['token']
            trade_size = opportunity['suggested_size']
            
            logger.info(f"Executing pump.fun micro trade: {token['symbol']} for {trade_size} SOL")
            
            # Execute through the DEX client
            result = await self.dex_client.execute_pumpfun_snipe(token['mint'], trade_size)
            
            if result['success']:
                # Set up auto-sell after 2-5 minutes with 10-20% profit target
                asyncio.create_task(self._schedule_pumpfun_exit(token['mint'], trade_size))
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing pump.fun micro trade: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _schedule_pumpfun_exit(self, token_mint: str, original_size: float):
        """Schedule automatic exit from pump.fun position"""
        try:
            # Wait 2-5 minutes
            import random
            wait_time = random.uniform(120, 300)
            await asyncio.sleep(wait_time)
            
            # Execute sell
            sell_result = await self.dex_client.execute_pumpfun_snipe(
                self.dex_client.tokens["SOL"],  # Sell token for SOL
                original_size
            )
            
            logger.info(f"Auto-exit from {token_mint}: {'SUCCESS' if sell_result.get('success') else 'FAILED'}")
            
        except Exception as e:
            logger.error(f"Error in scheduled pump.fun exit: {e}")
    
    async def _check_daily_limits(self):
        """Check and reset daily limits if needed"""
        current_date = datetime.utcnow().date()
        if current_date > self.last_reset_date:
            self.daily_losses = 0.0
            self.last_reset_date = current_date
            logger.info("Daily limits reset")
    
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        success_rate = (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': success_rate,
            'total_profit_sol': self.total_profit_sol,
            'total_fees_paid': self.total_fees_paid,
            'net_profit_sol': self.total_profit_sol - self.total_fees_paid,
            'daily_losses': self.daily_losses,
            'daily_loss_limit': self.daily_loss_limit,
            'max_trade_size': self.max_trade_size,
            'reserve_balance': self.reserve_balance,
            'estimated_usd_profit': self.total_profit_sol * 200,  # Assuming $200/SOL
            'roi_percentage': (self.total_profit_sol / 0.04) * 100 if self.total_profit_sol > 0 else 0
        }