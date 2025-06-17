import asyncio
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from .solana_client import SolanaClient
from .mev_strategies import MEVStrategies, ArbitrageOpportunity, TokenLaunch

logger = logging.getLogger(__name__)

class MEVBot:
    """Main MEV Bot orchestrator that manages all strategies"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.solana_client = SolanaClient()
        self.strategies = MEVStrategies(self.solana_client)
        self.is_running = False
        self.wallet_address = os.getenv("WALLET_ADDRESS")
        self.wallet_balance = 0.0
        
        # Bot configuration
        self.config = {
            "scan_interval": int(os.getenv("SCAN_INTERVAL", "5")),  # seconds
            "max_concurrent_trades": int(os.getenv("MAX_CONCURRENT_TRADES", "3")),
            "stop_loss_percentage": float(os.getenv("STOP_LOSS_PERCENTAGE", "5.0")),
            "take_profit_percentage": float(os.getenv("TAKE_PROFIT_PERCENTAGE", "10.0")),
            "enabled_strategies": os.getenv("ENABLED_STRATEGIES", "arbitrage,token_snipe").split(",")
        }
        
        # Real-time data
        self.current_opportunities = []
        self.active_positions = []
        self.recent_trades = []
        
        # Performance metrics
        self.session_stats = {
            "start_time": datetime.utcnow(),
            "total_scans": 0,
            "opportunities_found": 0,
            "trades_executed": 0,
            "profit_loss": 0.0,
            "largest_profit": 0.0,
            "largest_loss": 0.0,
            "success_rate": 0.0
        }
    
    async def start(self):
        """Start the MEV bot"""
        if self.is_running:
            logger.warning("Bot is already running")
            return
        
        logger.info("Starting MEV Bot...")
        self.is_running = True
        
        # Initialize wallet balance
        if self.wallet_address:
            self.wallet_balance = await self.solana_client.get_account_balance(self.wallet_address)
            logger.info(f"Wallet balance: {self.wallet_balance:.4f} SOL")
        
        # Start monitoring tasks
        tasks = []
        
        if "arbitrage" in self.config["enabled_strategies"]:
            tasks.append(asyncio.create_task(self._arbitrage_monitor()))
        
        if "token_snipe" in self.config["enabled_strategies"]:
            tasks.append(asyncio.create_task(self._token_snipe_monitor()))
        
        # Start performance tracking
        tasks.append(asyncio.create_task(self._performance_tracker()))
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in bot main loop: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the MEV bot"""
        logger.info("Stopping MEV Bot...")
        self.is_running = False
        
        # Close Solana client connections
        await self.solana_client.close()
        
        # Save final stats to database
        await self._save_session_stats()
    
    async def _arbitrage_monitor(self):
        """Monitor and execute arbitrage opportunities"""
        logger.info("Starting arbitrage monitoring...")
        
        while self.is_running:
            try:
                # Scan for opportunities
                opportunities = await self.strategies.scan_arbitrage_opportunities()
                self.current_opportunities = opportunities
                self.session_stats["total_scans"] += 1
                self.session_stats["opportunities_found"] += len(opportunities)
                
                # Execute profitable opportunities
                for opportunity in opportunities:
                    if len(self.active_positions) >= self.config["max_concurrent_trades"]:
                        logger.info("Max concurrent trades reached, skipping...")
                        break
                    
                    # Check if opportunity is still valid and profitable
                    if self._is_opportunity_valid(opportunity):
                        success = await self.strategies.execute_arbitrage(opportunity)
                        if success:
                            self.session_stats["trades_executed"] += 1
                            await self._record_trade({
                                "id": str(uuid.uuid4()),
                                "type": "arbitrage",
                                "token": opportunity.token_symbol,
                                "profit": opportunity.profit_amount,
                                "timestamp": datetime.utcnow(),
                                "details": {
                                    "buy_dex": opportunity.buy_dex,
                                    "sell_dex": opportunity.sell_dex,
                                    "buy_price": opportunity.buy_price,
                                    "sell_price": opportunity.sell_price,
                                    "profit_percentage": opportunity.profit_percentage
                                }
                            })
                
                await asyncio.sleep(self.config["scan_interval"])
                
            except Exception as e:
                logger.error(f"Error in arbitrage monitor: {e}")
                await asyncio.sleep(self.config["scan_interval"])
    
    async def _token_snipe_monitor(self):
        """Monitor and execute token sniping opportunities"""
        logger.info("Starting token snipe monitoring...")
        
        while self.is_running:
            try:
                # Monitor for new token launches
                launches = await self.strategies.monitor_new_token_launches()
                
                for launch in launches:
                    if len(self.active_positions) >= self.config["max_concurrent_trades"]:
                        break
                    
                    # Execute snipe if conditions are met
                    success = await self.strategies.execute_token_snipe(launch)
                    if success:
                        self.session_stats["trades_executed"] += 1
                        await self._record_trade({
                            "id": str(uuid.uuid4()),
                            "type": "token_snipe",
                            "token": launch.symbol,
                            "timestamp": datetime.utcnow(),
                            "details": {
                                "mint_address": launch.mint_address,
                                "initial_price": launch.initial_price,
                                "risk_score": launch.risk_score
                            }
                        })
                
                await asyncio.sleep(self.config["scan_interval"] * 2)  # Less frequent than arbitrage
                
            except Exception as e:
                logger.error(f"Error in token snipe monitor: {e}")
                await asyncio.sleep(self.config["scan_interval"])
    
    async def _performance_tracker(self):
        """Track and update performance metrics"""
        while self.is_running:
            try:
                # Update wallet balance
                if self.wallet_address:
                    new_balance = await self.solana_client.get_account_balance(self.wallet_address)
                    balance_change = new_balance - self.wallet_balance
                    self.session_stats["profit_loss"] += balance_change
                    self.wallet_balance = new_balance
                
                # Update success rate
                total_trades = self.session_stats["trades_executed"]
                if total_trades > 0:
                    successful_trades = self.strategies.successful_trades
                    self.session_stats["success_rate"] = (successful_trades / total_trades) * 100
                
                # Save stats periodically
                await self._save_session_stats()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in performance tracker: {e}")
                await asyncio.sleep(60)
    
    def _is_opportunity_valid(self, opportunity: ArbitrageOpportunity) -> bool:
        """Check if arbitrage opportunity is still valid"""
        # Check if opportunity is not too old
        age = datetime.utcnow() - opportunity.timestamp
        if age > timedelta(seconds=30):  # 30 seconds max age
            return False
        
        # Check if profit is still above minimum threshold
        if opportunity.profit_percentage < self.strategies.min_profit_percentage:
            return False
        
        return True
    
    async def _record_trade(self, trade_data: Dict):
        """Record trade in database and update recent trades"""
        try:
            # Save to database
            await self.db.trades.insert_one(trade_data)
            
            # Update recent trades list
            self.recent_trades.append(trade_data)
            if len(self.recent_trades) > 50:  # Keep only last 50 trades
                self.recent_trades = self.recent_trades[-50:]
            
            # Update profit tracking
            if "profit" in trade_data:
                profit = trade_data["profit"]
                if profit > self.session_stats["largest_profit"]:
                    self.session_stats["largest_profit"] = profit
                elif profit < 0 and abs(profit) > self.session_stats["largest_loss"]:
                    self.session_stats["largest_loss"] = abs(profit)
            
        except Exception as e:
            logger.error(f"Error recording trade: {e}")
    
    async def _save_session_stats(self):
        """Save current session statistics to database"""
        try:
            stats_record = {
                "session_id": f"session_{int(self.session_stats['start_time'].timestamp())}",
                "timestamp": datetime.utcnow(),
                "stats": self.session_stats,
                "config": self.config,
                "wallet_balance": self.wallet_balance
            }
            
            # Upsert session stats
            await self.db.bot_sessions.replace_one(
                {"session_id": stats_record["session_id"]},
                stats_record,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving session stats: {e}")
    
    def get_current_status(self) -> Dict:
        """Get current bot status and performance"""
        return {
            "is_running": self.is_running,
            "wallet_address": self.wallet_address,
            "wallet_balance": self.wallet_balance,
            "current_opportunities": len(self.current_opportunities),
            "active_positions": len(self.active_positions),
            "session_stats": self.session_stats,
            "recent_trades": self.recent_trades[-10:],  # Last 10 trades
            "config": self.config,
            "strategies_performance": self.strategies.get_performance_stats()
        }
    
    async def update_config(self, new_config: Dict):
        """Update bot configuration"""
        try:
            self.config.update(new_config)
            logger.info(f"Bot configuration updated: {new_config}")
            
            # Save updated config
            await self.db.bot_config.replace_one(
                {"type": "current_config"},
                {"type": "current_config", "config": self.config, "updated_at": datetime.utcnow()},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
    
    async def get_trade_history(self, limit: int = 100) -> List[Dict]:
        """Get trade history from database"""
        try:
            cursor = self.db.trades.find().sort("timestamp", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return []
    
    async def force_stop_all_positions(self):
        """Emergency stop - close all active positions"""
        logger.warning("Force stopping all positions!")
        
        try:
            # In production, this would close all open positions
            # For now, just clear the active positions list
            self.active_positions.clear()
            
            # Record emergency stop
            await self._record_trade({
                "id": str(uuid.uuid4()),
                "type": "emergency_stop",
                "timestamp": datetime.utcnow(),
                "details": {"reason": "Manual emergency stop"}
            })
            
        except Exception as e:
            logger.error(f"Error in emergency stop: {e}")