#!/usr/bin/env python3
import requests
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL from the frontend .env file
BASE_URL = "https://222cd522-9954-4672-83d4-bf3c5eba7216.preview.emergentagent.com/api"

# Test wallet address (base58 format)
TEST_WALLET = "11111111111111111111111111111112"

def test_api_health():
    """Test the API health check endpoint"""
    logger.info("Testing API health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        response.raise_for_status()
        data = response.json()
        
        assert "message" in data, "Response missing 'message' field"
        assert "Solana MEV Bot API" in data["message"], "API message doesn't match expected value"
        assert "version" in data, "Response missing 'version' field"
        assert "status" in data, "Response missing 'status' field"
        
        logger.info(f"✅ API health check passed: {data}")
        return True
    except Exception as e:
        logger.error(f"❌ API health check failed: {e}")
        return False

def test_bot_setup():
    """Test the bot setup endpoint"""
    logger.info("Testing bot setup...")
    
    try:
        payload = {
            "wallet_address": TEST_WALLET,
            "rpc_endpoint": "https://api.mainnet-beta.solana.com"
        }
        
        response = requests.post(f"{BASE_URL}/bot/setup", json=payload)
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] == "success", f"Setup failed with status: {data.get('status')}"
        assert "wallet_address" in data, "Response missing 'wallet_address' field"
        assert data["wallet_address"] == TEST_WALLET, "Wallet address in response doesn't match"
        
        logger.info(f"✅ Bot setup passed: {data}")
        return True
    except Exception as e:
        logger.error(f"❌ Bot setup failed: {e}")
        return False

def test_bot_start():
    """Test the bot start endpoint"""
    logger.info("Testing bot start...")
    
    try:
        response = requests.post(f"{BASE_URL}/bot/start")
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] in ["success", "already_running"], f"Start failed with status: {data.get('status')}"
        
        logger.info(f"✅ Bot start passed: {data}")
        return True
    except Exception as e:
        logger.error(f"❌ Bot start failed: {e}")
        return False

def test_bot_status():
    """Test the bot status endpoint"""
    logger.info("Testing bot status...")
    
    try:
        response = requests.get(f"{BASE_URL}/bot/status")
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        
        if data["status"] == "not_initialized":
            logger.warning("Bot not initialized, setup required before status check")
            return False
        
        assert "data" in data, "Response missing 'data' field"
        status_data = data["data"]
        
        assert "is_running" in status_data, "Status missing 'is_running' field"
        assert "wallet_balance" in status_data, "Status missing 'wallet_balance' field"
        assert "session_stats" in status_data, "Status missing 'session_stats' field"
        
        logger.info(f"✅ Bot status passed: {data['status']}")
        return True
    except Exception as e:
        logger.error(f"❌ Bot status failed: {e}")
        return False

def test_bot_opportunities():
    """Test the bot opportunities endpoint"""
    logger.info("Testing bot opportunities...")
    
    try:
        response = requests.get(f"{BASE_URL}/bot/opportunities")
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert "opportunities" in data, "Response missing 'opportunities' field"
        assert "count" in data, "Response missing 'count' field"
        assert isinstance(data["opportunities"], list), "Opportunities should be a list"
        
        logger.info(f"✅ Bot opportunities passed: {len(data['opportunities'])} opportunities found")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "Bot not initialized" in e.response.text:
            logger.warning("Bot not initialized, setup required before checking opportunities")
            return False
        logger.error(f"❌ Bot opportunities failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Bot opportunities failed: {e}")
        return False

def test_bot_trades():
    """Test the bot trades endpoint"""
    logger.info("Testing bot trades...")
    
    try:
        response = requests.get(f"{BASE_URL}/bot/trades")
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert "trades" in data, "Response missing 'trades' field"
        assert "count" in data, "Response missing 'count' field"
        assert isinstance(data["trades"], list), "Trades should be a list"
        
        logger.info(f"✅ Bot trades passed: {len(data['trades'])} trades found")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "Bot not initialized" in e.response.text:
            logger.warning("Bot not initialized, setup required before checking trades")
            return False
        logger.error(f"❌ Bot trades failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Bot trades failed: {e}")
        return False

def test_bot_wallet_balance():
    """Test the wallet balance endpoint"""
    logger.info("Testing wallet balance...")
    
    try:
        response = requests.get(f"{BASE_URL}/bot/wallet-balance")
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert "wallet_address" in data, "Response missing 'wallet_address' field"
        assert "sol_balance" in data, "Response missing 'sol_balance' field"
        assert "token_accounts" in data, "Response missing 'token_accounts' field"
        
        logger.info(f"✅ Wallet balance passed: {data['sol_balance']} SOL")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "Bot not initialized" in e.response.text:
            logger.warning("Bot not initialized, setup required before checking wallet balance")
            return False
        logger.error(f"❌ Wallet balance failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Wallet balance failed: {e}")
        return False

def test_bot_config_update():
    """Test the bot configuration update endpoint"""
    logger.info("Testing bot config update...")
    
    try:
        payload = {
            "scan_interval": 10,
            "max_concurrent_trades": 2,
            "stop_loss_percentage": 3.0,
            "take_profit_percentage": 15.0,
            "min_profit_percentage": 0.8,
            "max_position_size": 0.5,
            "enabled_strategies": ["arbitrage"]
        }
        
        response = requests.put(f"{BASE_URL}/bot/config", json=payload)
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] == "success", f"Config update failed with status: {data.get('status')}"
        assert "config" in data, "Response missing 'config' field"
        
        config = data["config"]
        assert config["scan_interval"] == payload["scan_interval"], "scan_interval not updated correctly"
        assert config["max_concurrent_trades"] == payload["max_concurrent_trades"], "max_concurrent_trades not updated correctly"
        
        logger.info(f"✅ Bot config update passed")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "Bot not initialized" in e.response.text:
            logger.warning("Bot not initialized, setup required before updating config")
            return False
        logger.error(f"❌ Bot config update failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Bot config update failed: {e}")
        return False

def test_bot_stop():
    """Test the bot stop endpoint"""
    logger.info("Testing bot stop...")
    
    try:
        response = requests.post(f"{BASE_URL}/bot/stop")
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] in ["success", "already_stopped"], f"Stop failed with status: {data.get('status')}"
        
        logger.info(f"✅ Bot stop passed: {data}")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "Bot not initialized" in e.response.text:
            logger.warning("Bot not initialized, setup required before stopping")
            return False
        logger.error(f"❌ Bot stop failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Bot stop failed: {e}")
        return False

def test_bot_emergency_stop():
    """Test the bot emergency stop endpoint"""
    logger.info("Testing bot emergency stop...")
    
    try:
        response = requests.post(f"{BASE_URL}/bot/emergency-stop")
        response.raise_for_status()
        data = response.json()
        
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] == "success", f"Emergency stop failed with status: {data.get('status')}"
        assert "message" in data, "Response missing 'message' field"
        
        logger.info(f"✅ Bot emergency stop passed: {data}")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "Bot not initialized" in e.response.text:
            logger.warning("Bot not initialized, setup required before emergency stop")
            return False
        logger.error(f"❌ Bot emergency stop failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Bot emergency stop failed: {e}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    logger.info("Starting Solana MEV Bot API tests...")
    
    results = {}
    
    # Test API health
    results["API Health Check"] = test_api_health()
    
    # Test bot setup
    results["Bot Setup"] = test_bot_setup()
    
    # Test bot start
    if results["Bot Setup"]:
        results["Bot Start"] = test_bot_start()
    else:
        logger.warning("Skipping Bot Start test due to setup failure")
        results["Bot Start"] = False
    
    # Test bot status
    if results["Bot Setup"]:
        results["Bot Status"] = test_bot_status()
    else:
        logger.warning("Skipping Bot Status test due to setup failure")
        results["Bot Status"] = False
    
    # Test opportunities
    if results["Bot Setup"] and results["Bot Start"]:
        results["Bot Opportunities"] = test_bot_opportunities()
    else:
        logger.warning("Skipping Bot Opportunities test due to setup or start failure")
        results["Bot Opportunities"] = False
    
    # Test trades
    if results["Bot Setup"] and results["Bot Start"]:
        results["Bot Trades"] = test_bot_trades()
    else:
        logger.warning("Skipping Bot Trades test due to setup or start failure")
        results["Bot Trades"] = False
    
    # Test wallet balance
    if results["Bot Setup"]:
        results["Wallet Balance"] = test_bot_wallet_balance()
    else:
        logger.warning("Skipping Wallet Balance test due to setup failure")
        results["Wallet Balance"] = False
    
    # Test config update
    if results["Bot Setup"]:
        results["Config Update"] = test_bot_config_update()
    else:
        logger.warning("Skipping Config Update test due to setup failure")
        results["Config Update"] = False
    
    # Test bot stop
    if results["Bot Setup"] and results["Bot Start"]:
        results["Bot Stop"] = test_bot_stop()
    else:
        logger.warning("Skipping Bot Stop test due to setup or start failure")
        results["Bot Stop"] = False
    
    # Test emergency stop
    if results["Bot Setup"]:
        results["Emergency Stop"] = test_bot_emergency_stop()
    else:
        logger.warning("Skipping Emergency Stop test due to setup failure")
        results["Emergency Stop"] = False
    
    # Print summary
    logger.info("\n=== TEST RESULTS SUMMARY ===")
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED! The Solana MEV Bot API is working correctly.")
    else:
        logger.error("\n❌ SOME TESTS FAILED. Please check the logs for details.")
    
    return results

if __name__ == "__main__":
    run_all_tests()