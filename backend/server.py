from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import asyncio

# Import MEV Bot components
from .mev_bot import MEVBot
from .solana_client import SolanaClient
from .mev_strategies import MEVStrategies
from .micro_mev_strategy import MicroMEVStrategy
from .advanced_dex_client import AdvancedDEXClient


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global MEV Bot instance
mev_bot: Optional[MEVBot] = None
micro_strategy: Optional[MicroMEVStrategy] = None

# Initialize micro strategy for $8 balance trading
async def init_micro_strategy():
    global micro_strategy
    try:
        micro_strategy = MicroMEVStrategy()
        logger.info("Micro MEV strategy initialized for small balance trading")
    except Exception as e:
        logger.error(f"Failed to initialize micro strategy: {e}")

@app.on_event("startup")
async def startup_event():
    await init_micro_strategy()

# MEV Bot Models
class BotConfig(BaseModel):
    scan_interval: int = 5
    max_concurrent_trades: int = 3
    stop_loss_percentage: float = 5.0
    take_profit_percentage: float = 10.0
    min_profit_percentage: float = 0.5
    max_position_size: float = 1.0
    enabled_strategies: List[str] = ["arbitrage", "token_snipe"]

class WalletSetup(BaseModel):
    wallet_address: str
    rpc_endpoint: Optional[str] = None
    private_rpc_endpoint: Optional[str] = None

class BotStatus(BaseModel):
    is_running: bool
    wallet_balance: float
    current_opportunities: int
    total_profit: float
    total_trades: int
    success_rate: float


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Solana MEV Bot API", "version": "1.0.0", "status": "active"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# MEV Bot Endpoints
@api_router.post("/bot/setup")
async def setup_bot(wallet_setup: WalletSetup):
    """Setup MEV bot with wallet and RPC configuration"""
    global mev_bot
    
    try:
        # Set environment variables
        os.environ["WALLET_ADDRESS"] = wallet_setup.wallet_address
        if wallet_setup.rpc_endpoint:
            os.environ["SOLANA_RPC_URL"] = wallet_setup.rpc_endpoint
        if wallet_setup.private_rpc_endpoint:
            os.environ["PRIVATE_RPC_URL"] = wallet_setup.private_rpc_endpoint
        
        # Initialize MEV bot
        mev_bot = MEVBot(db)
        
        return {
            "status": "success",
            "message": "MEV Bot setup completed",
            "wallet_address": wallet_setup.wallet_address
        }
        
    except Exception as e:
        logger.error(f"Error setting up bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/start")
async def start_bot(background_tasks: BackgroundTasks):
    """Start the MEV bot"""
    global mev_bot
    
    if not mev_bot:
        raise HTTPException(status_code=400, detail="Bot not setup. Please setup bot first.")
    
    if mev_bot.is_running:
        return {"status": "already_running", "message": "Bot is already running"}
    
    try:
        # Start bot in background
        background_tasks.add_task(mev_bot.start)
        
        return {
            "status": "success",
            "message": "MEV Bot started successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/stop")
async def stop_bot():
    """Stop the MEV bot"""
    global mev_bot
    
    if not mev_bot:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    if not mev_bot.is_running:
        return {"status": "already_stopped", "message": "Bot is not running"}
    
    try:
        await mev_bot.stop()
        
        return {
            "status": "success",
            "message": "MEV Bot stopped successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/status")
async def get_bot_status():
    """Get current bot status and performance metrics"""
    global mev_bot
    
    if not mev_bot:
        return {
            "status": "not_initialized",
            "message": "Bot not setup yet",
            "is_running": False
        }
    
    try:
        status = mev_bot.get_current_status()
        return {
            "status": "success",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/opportunities")
async def get_current_opportunities():
    """Get current arbitrage opportunities"""
    global mev_bot
    
    if not mev_bot:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    try:
        opportunities = []
        for opp in mev_bot.current_opportunities:
            opportunities.append({
                "token_symbol": opp.token_symbol,
                "token_mint": opp.token_mint,
                "buy_dex": opp.buy_dex,
                "sell_dex": opp.sell_dex,
                "buy_price": opp.buy_price,
                "sell_price": opp.sell_price,
                "profit_percentage": opp.profit_percentage,
                "profit_amount": opp.profit_amount,
                "timestamp": opp.timestamp.isoformat()
            })
        
        return {
            "status": "success",
            "opportunities": opportunities,
            "count": len(opportunities)
        }
        
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/trades")
async def get_trade_history(limit: int = 50):
    """Get trade history"""
    global mev_bot
    
    if not mev_bot:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    try:
        trades = await mev_bot.get_trade_history(limit)
        return {
            "status": "success",
            "trades": trades,
            "count": len(trades)
        }
        
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/bot/config")
async def update_bot_config(config: BotConfig):
    """Update bot configuration"""
    global mev_bot
    
    if not mev_bot:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    try:
        config_dict = config.dict()
        await mev_bot.update_config(config_dict)
        
        return {
            "status": "success",
            "message": "Bot configuration updated",
            "config": config_dict
        }
        
    except Exception as e:
        logger.error(f"Error updating bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/emergency-stop")
async def emergency_stop():
    """Emergency stop - immediately close all positions"""
    global mev_bot
    
    if not mev_bot:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    try:
        await mev_bot.force_stop_all_positions()
        await mev_bot.stop()
        
        return {
            "status": "success",
            "message": "Emergency stop executed - all positions closed",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error in emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/wallet-balance")
async def get_wallet_balance():
    """Get current wallet balance"""
    global mev_bot
    
    if not mev_bot:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    try:
        wallet_address = os.getenv("WALLET_ADDRESS")
        if not wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address not configured")
        
        balance = await mev_bot.solana_client.get_account_balance(wallet_address)
        token_accounts = await mev_bot.solana_client.get_token_accounts(wallet_address)
        
        return {
            "status": "success",
            "wallet_address": wallet_address,
            "sol_balance": balance,
            "token_accounts": len(token_accounts),
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
