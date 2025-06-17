import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BotStatus from './BotStatus';
import WalletSetup from './WalletSetup';
import TradingMetrics from './TradingMetrics';
import OpportunitiesPanel from './OpportunitiesPanel';
import TradeHistory from './TradeHistory';
import BotControls from './BotControls';
import PumpFunPanel from './PumpFunPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [botStatus, setBotStatus] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [trades, setTrades] = useState([]);
  const [walletBalance, setWalletBalance] = useState(null);
  const [isSetup, setIsSetup] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch bot status
  const fetchBotStatus = async () => {
    try {
      const response = await axios.get(`${API}/bot/status`);
      setBotStatus(response.data.data);
      setIsSetup(response.data.data && response.data.data.wallet_address);
    } catch (error) {
      if (error.response?.status === 400) {
        setIsSetup(false);
      } else {
        setError('Failed to fetch bot status');
      }
    }
  };

  // Fetch opportunities
  const fetchOpportunities = async () => {
    try {
      const response = await axios.get(`${API}/bot/opportunities`);
      if (response.data.status === 'success') {
        setOpportunities(response.data.opportunities);
      }
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
    }
  };

  // Fetch trade history
  const fetchTrades = async () => {
    try {
      const response = await axios.get(`${API}/bot/trades?limit=20`);
      if (response.data.status === 'success') {
        setTrades(response.data.trades);
      }
    } catch (error) {
      console.error('Failed to fetch trades:', error);
    }
  };

  // Fetch wallet balance
  const fetchWalletBalance = async () => {
    try {
      const response = await axios.get(`${API}/bot/wallet-balance`);
      if (response.data.status === 'success') {
        setWalletBalance(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch wallet balance:', error);
    }
  };

  // Initial load
  useEffect(() => {
    const initializeDashboard = async () => {
      setLoading(true);
      await fetchBotStatus();
      setLoading(false);
    };

    initializeDashboard();
  }, []);

  // Auto-refresh data when bot is running
  useEffect(() => {
    if (botStatus?.is_running) {
      const interval = setInterval(() => {
        fetchBotStatus();
        fetchOpportunities();
        fetchTrades();
        fetchWalletBalance();
      }, 5000); // Refresh every 5 seconds

      return () => clearInterval(interval);
    }
  }, [botStatus?.is_running]);

  // Handle bot setup completion
  const handleSetupComplete = () => {
    setIsSetup(true);
    fetchBotStatus();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-400"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-green-400 mb-2">
            Solana MEV Bot Dashboard
          </h1>
          <p className="text-gray-400">
            Advanced Maximum Extractable Value Trading Bot
          </p>
        </div>

        {!isSetup ? (
          <WalletSetup onSetupComplete={handleSetupComplete} />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Bot Status and Controls */}
            <div className="lg:col-span-1 space-y-6">
              <BotStatus 
                status={botStatus} 
                walletBalance={walletBalance}
                onRefresh={fetchBotStatus}
              />
              <BotControls 
                botStatus={botStatus}
                onStatusChange={fetchBotStatus}
              />
            </div>

            {/* Middle Column - Trading Metrics and Opportunities */}
            <div className="lg:col-span-1 space-y-6">
              <TradingMetrics 
                status={botStatus}
                trades={trades}
              />
              <OpportunitiesPanel 
                opportunities={opportunities}
                isRunning={botStatus?.is_running}
              />
            </div>

            {/* Right Column - Trade History */}
            <div className="lg:col-span-1">
              <TradeHistory 
                trades={trades}
                onRefresh={fetchTrades}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;