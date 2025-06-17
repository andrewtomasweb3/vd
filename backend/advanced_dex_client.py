import asyncio
import logging
import aiohttp
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import os

logger = logging.getLogger(__name__)

class AdvancedDEXClient:
    """Enhanced DEX client for Raydium, Meteora, PumpFun trading"""
    
    def __init__(self, rpc_url: str, private_key_bs58: str):
        self.rpc_url = rpc_url
        self.private_key_bs58 = private_key_bs58
        self.keypair = None
        self.wallet_pubkey = None
        
        # Initialize wallet
        try:
            private_key_bytes = base58.b58decode(private_key_bs58)
            self.keypair = Keypair.from_bytes(private_key_bytes)
            self.wallet_pubkey = self.keypair.pubkey()
            logger.info(f"Wallet initialized: {str(self.wallet_pubkey)}")
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {e}")
        
        # DEX Program IDs
        self.dex_programs = {
            "raydium_amm": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
            "raydium_cpmm": "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",
            "meteora_dlmm": "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
            "pumpfun": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
            "jupiter": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
        }
        
        # Token addresses for trading
        self.tokens = {
            "SOL": "So11111111111111111111111111111111111111112",
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "WSOL": "So11111111111111111111111111111111111111112"
        }
    
    async def get_pumpfun_tokens(self) -> List[Dict]:
        """Get trending/new tokens from pump.fun"""
        try:
            async with aiohttp.ClientSession() as session:
                # Pump.fun API endpoint
                url = "https://frontend-api.pump.fun/coins?offset=0&limit=20&sort=created_timestamp&order=DESC&includeNsfw=false"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Filter for recently created tokens with good metrics
                        filtered_tokens = []
                        for token in data:
                            if (token.get('market_cap', 0) > 10000 and 
                                token.get('market_cap', 0) < 1000000 and
                                token.get('reply_count', 0) > 5):
                                
                                filtered_tokens.append({
                                    'mint': token['mint'],
                                    'name': token['name'],
                                    'symbol': token['symbol'],
                                    'market_cap': token['market_cap'],
                                    'price': token.get('usd_market_cap', 0) / token.get('market_cap', 1),
                                    'created_timestamp': token['created_timestamp'],
                                    'reply_count': token['reply_count']
                                })
                        
                        return filtered_tokens[:5]  # Top 5 candidates
            
            return []
        except Exception as e:
            logger.error(f"Error fetching pump.fun tokens: {e}")
            return []
    
    async def get_raydium_pools(self) -> Dict[str, Dict]:
        """Get Raydium pool information for arbitrage"""
        try:
            async with aiohttp.ClientSession() as session:
                # Raydium pools API
                url = "https://api.raydium.io/v2/sdk/liquidity/mainnet.json"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Filter for SOL/USDC and high-volume pools
                        relevant_pools = {}
                        for pool_id, pool_data in data['official'].items():
                            if (pool_data['baseMint'] in self.tokens.values() or
                                pool_data['quoteMint'] in self.tokens.values()):
                                
                                relevant_pools[pool_id] = {
                                    'baseMint': pool_data['baseMint'],
                                    'quoteMint': pool_data['quoteMint'],
                                    'baseReserve': pool_data.get('baseReserve', 0),
                                    'quoteReserve': pool_data.get('quoteReserve', 0),
                                    'lpMint': pool_data['lpMint']
                                }
                        
                        return relevant_pools
            
            return {}
        except Exception as e:
            logger.error(f"Error fetching Raydium pools: {e}")
            return {}
    
    async def get_meteora_pools(self) -> Dict[str, Dict]:
        """Get Meteora DLMM pools for trading"""
        try:
            async with aiohttp.ClientSession() as session:
                # Meteora pools API
                url = "https://dlmm-api.meteora.ag/pair/all"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Filter for relevant pairs
                        relevant_pools = {}
                        for pair in data:
                            if (pair['mint_x'] in self.tokens.values() or
                                pair['mint_y'] in self.tokens.values()):
                                
                                relevant_pools[pair['address']] = {
                                    'mintX': pair['mint_x'],
                                    'mintY': pair['mint_y'],
                                    'reserveX': pair.get('reserve_x', 0),
                                    'reserveY': pair.get('reserve_y', 0),
                                    'fees': pair.get('fee_rate', 0)
                                }
                        
                        return relevant_pools
            
            return {}
        except Exception as e:
            logger.error(f"Error fetching Meteora pools: {e}")
            return {}
    
    async def calculate_arbitrage_opportunities(self) -> List[Dict]:
        """Find arbitrage opportunities across all DEXs"""
        opportunities = []
        
        try:
            # Get pool data from all DEXs
            raydium_pools = await self.get_raydium_pools()
            meteora_pools = await self.get_meteora_pools()
            
            # Compare prices between DEXs for same token pairs
            for token_pair in [("SOL", "USDC")]:
                base_token, quote_token = token_pair
                base_mint = self.tokens[base_token]
                quote_mint = self.tokens[quote_token]
                
                # Find pools for this pair across DEXs
                raydium_price = await self._get_pool_price(raydium_pools, base_mint, quote_mint)
                meteora_price = await self._get_pool_price(meteora_pools, base_mint, quote_mint)
                
                if raydium_price and meteora_price:
                    price_diff = abs(raydium_price - meteora_price) / min(raydium_price, meteora_price)
                    
                    if price_diff > 0.01:  # 1% minimum profit
                        buy_dex = "raydium" if raydium_price < meteora_price else "meteora"
                        sell_dex = "meteora" if buy_dex == "raydium" else "raydium"
                        buy_price = min(raydium_price, meteora_price)
                        sell_price = max(raydium_price, meteora_price)
                        
                        opportunities.append({
                            'token_pair': f"{base_token}/{quote_token}",
                            'buy_dex': buy_dex,
                            'sell_dex': sell_dex,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'profit_percentage': price_diff * 100,
                            'estimated_profit': (sell_price - buy_price) * 0.01,  # For 0.01 SOL trade
                            'timestamp': datetime.utcnow()
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error calculating arbitrage opportunities: {e}")
            return []
    
    async def _get_pool_price(self, pools: Dict, base_mint: str, quote_mint: str) -> Optional[float]:
        """Calculate price from pool reserves"""
        try:
            for pool_data in pools.values():
                if ((pool_data.get('baseMint') == base_mint and pool_data.get('quoteMint') == quote_mint) or
                    (pool_data.get('mintX') == base_mint and pool_data.get('mintY') == quote_mint)):
                    
                    base_reserve = pool_data.get('baseReserve') or pool_data.get('reserveX', 0)
                    quote_reserve = pool_data.get('quoteReserve') or pool_data.get('reserveY', 0)
                    
                    if base_reserve > 0 and quote_reserve > 0:
                        return float(quote_reserve) / float(base_reserve)
            
            return None
        except Exception as e:
            logger.error(f"Error calculating pool price: {e}")
            return None
    
    async def execute_pumpfun_snipe(self, token_mint: str, amount_sol: float) -> Dict:
        """Execute a pump.fun token snipe"""
        try:
            logger.info(f"Attempting to snipe {token_mint} with {amount_sol} SOL")
            
            # For demo purposes - in production, this would execute actual swap
            # Using Jupiter API for pump.fun token swaps
            swap_result = await self._execute_jupiter_swap(
                input_mint=self.tokens["SOL"],
                output_mint=token_mint,
                amount=int(amount_sol * 1e9),  # Convert to lamports
                slippage_bps=300  # 3% slippage for new tokens
            )
            
            return {
                'success': swap_result is not None,
                'transaction_signature': swap_result,
                'token_mint': token_mint,
                'amount_sol': amount_sol,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error executing pump.fun snipe: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_jupiter_swap(self, input_mint: str, output_mint: str, amount: int, slippage_bps: int = 50) -> Optional[str]:
        """Execute swap through Jupiter aggregator"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get quote from Jupiter
                quote_url = f"https://quote-api.jup.ag/v6/quote"
                quote_params = {
                    'inputMint': input_mint,
                    'outputMint': output_mint,
                    'amount': amount,
                    'slippageBps': slippage_bps,
                    'onlyDirectRoutes': 'false',
                    'asLegacyTransaction': 'false'
                }
                
                async with session.get(quote_url, params=quote_params) as response:
                    if response.status != 200:
                        logger.error(f"Jupiter quote failed: {response.status}")
                        return None
                    
                    quote_data = await response.json()
                    
                    # For demo purposes, return a mock transaction signature
                    # In production, you would use the quote to create and send the actual transaction
                    return f"jupiter_swap_{int(datetime.utcnow().timestamp())}"
            
        except Exception as e:
            logger.error(f"Error executing Jupiter swap: {e}")
            return None
    
    async def get_wallet_balance(self) -> float:
        """Get current SOL balance"""
        try:
            # In production, this would query the actual balance
            # For demo, return a simulated balance based on $8 USD (~0.04 SOL at $200/SOL)
            return 0.04
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return 0.0
    
    async def estimate_transaction_fee(self, instruction_count: int = 1) -> float:
        """Estimate transaction fees"""
        # Base fee per signature + compute unit fees
        base_fee = 0.000005  # 5000 lamports
        compute_fee = instruction_count * 0.000001  # Estimated compute cost
        
        return base_fee + compute_fee
    
    async def check_profitable_trade(self, profit_sol: float, gas_fee: float) -> bool:
        """Check if trade is profitable after fees"""
        net_profit = profit_sol - gas_fee
        return net_profit > 0.001  # Minimum 0.001 SOL profit ($0.20 at $200/SOL)