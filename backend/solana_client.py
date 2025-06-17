import asyncio
import logging
from typing import Dict, List, Optional, Any
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import RPCResponse
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import aiohttp
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class SolanaClient:
    """Enhanced Solana RPC client for MEV operations with multiple endpoints"""
    
    def __init__(self):
        # Default to public RPC, but can be configured for private endpoints
        self.rpc_endpoint = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.private_rpc = os.getenv("PRIVATE_RPC_URL")  # For faster execution
        self.client = AsyncClient(self.rpc_endpoint)
        self.private_client = AsyncClient(self.private_rpc) if self.private_rpc else None
        
        # Known DEX program IDs for arbitrage
        self.dex_programs = {
            "raydium": PublicKey("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"),
            "orca": PublicKey("9W959DqEETiGZocYWCQPaJ6sKoAz6Jv4gG5JMhH2q1Gg"),
            "serum": PublicKey("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"),
            "jupiter": PublicKey("JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"),
        }
        
        # Major token addresses
        self.tokens = {
            "SOL": PublicKey("So11111111111111111111111111111111111111112"),
            "USDC": PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
            "USDT": PublicKey("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"),
            "RAY": PublicKey("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"),
            "SRM": PublicKey("SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt"),
        }
    
    async def get_token_price(self, token_address: str, dex: str = "jupiter") -> Optional[float]:
        """Get current token price from DEX"""
        try:
            if dex == "jupiter":
                # Use Jupiter price API
                async with aiohttp.ClientSession() as session:
                    url = f"https://price.jup.ag/v4/price?ids={token_address}"
                    async with session.get(url) as response:
                        data = await response.json()
                        if "data" in data and token_address in data["data"]:
                            return float(data["data"][token_address]["price"])
            
            # Fallback to on-chain price calculation
            return await self._get_onchain_price(token_address)
            
        except Exception as e:
            logger.error(f"Error getting price for {token_address}: {e}")
            return None
    
    async def _get_onchain_price(self, token_address: str) -> Optional[float]:
        """Calculate price from on-chain data"""
        try:
            # This would involve reading from AMM pools
            # Simplified implementation - in production, read from actual pool data
            return None
        except Exception as e:
            logger.error(f"Error calculating on-chain price: {e}")
            return None
    
    async def get_recent_blockhash(self) -> str:
        """Get recent blockhash for transaction"""
        try:
            response = await self.client.get_latest_blockhash()
            return str(response.value.blockhash)
        except Exception as e:
            logger.error(f"Error getting blockhash: {e}")
            raise
    
    async def simulate_transaction(self, transaction: Transaction) -> bool:
        """Simulate transaction to check if it will succeed"""
        try:
            response = await self.client.simulate_transaction(transaction)
            return response.value.err is None
        except Exception as e:
            logger.error(f"Error simulating transaction: {e}")
            return False
    
    async def send_transaction_fast(self, transaction: Transaction) -> Optional[str]:
        """Send transaction using private RPC for faster execution"""
        try:
            client = self.private_client if self.private_client else self.client
            
            # First simulate
            if not await self.simulate_transaction(transaction):
                logger.warning("Transaction simulation failed")
                return None
            
            # Send transaction
            response = await client.send_transaction(transaction)
            return str(response.value)
            
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            return None
    
    async def get_token_accounts(self, wallet_address: str) -> List[Dict]:
        """Get all token accounts for wallet"""
        try:
            response = await self.client.get_token_accounts_by_owner(
                PublicKey(wallet_address),
                {"programId": PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")}
            )
            return response.value if response.value else []
        except Exception as e:
            logger.error(f"Error getting token accounts: {e}")
            return []
    
    async def get_account_balance(self, address: str) -> float:
        """Get SOL balance for address"""
        try:
            response = await self.client.get_balance(PublicKey(address))
            return response.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0
    
    async def monitor_new_tokens(self, callback) -> None:
        """Monitor for new token launches"""
        try:
            # Subscribe to program account changes for token program
            # This is a simplified version - production would use WebSocket subscriptions
            while True:
                # Check for new token mints
                await asyncio.sleep(1)  # Poll every second
                # Call callback with new token data
                
        except Exception as e:
            logger.error(f"Error monitoring new tokens: {e}")
    
    async def get_dex_prices(self, token_mint: str) -> Dict[str, float]:
        """Get token prices from multiple DEXs for arbitrage detection"""
        prices = {}
        
        for dex_name in ["raydium", "orca", "serum"]:
            try:
                price = await self.get_token_price(token_mint, dex_name)
                if price:
                    prices[dex_name] = price
            except Exception as e:
                logger.error(f"Error getting {dex_name} price: {e}")
        
        return prices
    
    async def close(self):
        """Close client connections"""
        if self.client:
            await self.client.close()
        if self.private_client:
            await self.private_client.close()