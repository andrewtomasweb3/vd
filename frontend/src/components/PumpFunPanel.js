import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PumpFunPanel = ({ isRunning }) => {
  const [opportunities, setOpportunities] = useState([]);
  const [microOpportunities, setMicroOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(null);

  // Fetch opportunities
  const fetchOpportunities = async () => {
    if (!isRunning) return;
    
    try {
      const [pumpResponse, microResponse] = await Promise.all([
        axios.get(`${API}/bot/pumpfun-opportunities`),
        axios.get(`${API}/bot/micro-opportunities`)
      ]);
      
      if (pumpResponse.data.status === 'success') {
        setOpportunities(pumpResponse.data.opportunities);
      }
      
      if (microResponse.data.status === 'success') {
        setMicroOpportunities(microResponse.data.opportunities);
      }
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
    }
  };

  // Auto-refresh when running
  useEffect(() => {
    if (isRunning) {
      fetchOpportunities();
      const interval = setInterval(fetchOpportunities, 5000);
      return () => clearInterval(interval);
    }
  }, [isRunning]);

  // Execute pump.fun trade
  const executePumpFunTrade = async (opportunity) => {
    setExecuting(opportunity.token.mint);
    
    try {
      const response = await axios.post(`${API}/bot/execute-pumpfun-trade`, {
        token_mint: opportunity.token.mint
      });
      
      if (response.data.status === 'success') {
        alert(`✅ Pump.fun trade executed successfully for ${opportunity.token.symbol}!`);
      } else {
        alert(`❌ Trade failed: ${response.data.result?.error || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`❌ Trade failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExecuting(null);
      fetchOpportunities(); // Refresh data
    }
  };

  // Execute micro arbitrage
  const executeMicroArbitrage = async () => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/bot/execute-micro-arbitrage`);
      
      if (response.data.status === 'success') {
        const result = response.data.result;
        alert(`✅ Micro arbitrage successful!\nProfit: ${result.net_profit?.toFixed(6)} SOL\nPair: ${response.data.opportunity.token_pair}`);
      } else if (response.data.status === 'no_opportunities') {
        alert('ℹ️ No profitable opportunities available right now');
      } else {
        alert(`❌ Arbitrage failed: ${response.data.result?.reason || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`❌ Arbitrage failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
      fetchOpportunities(); // Refresh data
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getRiskColor = (riskScore) => {
    if (riskScore <= 3) return 'text-green-400';
    if (riskScore <= 6) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-6">
      {/* Micro Arbitrage Section */}
      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">🔄 Micro Arbitrage ($8 Optimized)</h3>
          <button
            onClick={executeMicroArbitrage}
            disabled={loading || !isRunning || microOpportunities.length === 0}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              loading || !isRunning || microOpportunities.length === 0
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            } text-white`}
          >
            {loading ? '⏳ Executing...' : '🚀 Execute Best Opportunity'}
          </button>
        </div>

        <div className="space-y-3 max-h-64 overflow-y-auto">
          {microOpportunities.length > 0 ? (
            microOpportunities.map((opp, index) => (
              <div key={index} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white">{opp.token_pair}</span>
                  <span className="text-green-400 font-bold">
                    +{opp.profit_percentage.toFixed(2)}%
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-400">Route</div>
                    <div className="text-blue-400">{opp.buy_dex} → {opp.sell_dex}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Net Profit</div>
                    <div className="text-green-400 font-medium">
                      {opp.net_profit.toFixed(6)} SOL
                    </div>
                  </div>
                </div>
                
                <div className="mt-2 pt-2 border-t border-gray-600 text-xs text-gray-400">
                  Fees: {opp.estimated_fees.toFixed(6)} SOL | {formatTimestamp(opp.timestamp)}
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-6 text-gray-400">
              {isRunning ? 'Scanning for micro arbitrage opportunities...' : 'Start bot to scan for opportunities'}
            </div>
          )}
        </div>
      </div>

      {/* Pump.fun Section */}
      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">🎯 Pump.fun Sniping</h3>
          <div className="flex items-center space-x-2">
            {isRunning && (
              <div className="flex items-center">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse mr-2"></div>
                <span className="text-xs text-purple-400">Live Feed</span>
              </div>
            )}
            <span className="text-sm text-gray-400">
              {opportunities.length} tokens
            </span>
          </div>
        </div>

        <div className="space-y-3 max-h-80 overflow-y-auto">
          {opportunities.length > 0 ? (
            opportunities.map((opp, index) => (
              <div key={index} className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-semibold text-white">{opp.token.symbol}</div>
                    <div className="text-sm text-gray-400">{opp.token.name}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${getRiskColor(opp.risk_score)}`}>
                      Risk: {opp.risk_score}/10
                    </div>
                    <div className="text-sm text-gray-400">
                      ${(opp.token.market_cap / 1000).toFixed(0)}k mcap
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-3 text-sm">
                  <div>
                    <div className="text-gray-400">Trade Size</div>
                    <div className="text-green-400 font-medium">
                      {opp.suggested_size.toFixed(4)} SOL
                    </div>
                    <div className="text-gray-500 text-xs">
                      ${(opp.suggested_size * 200).toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-400">Replies</div>
                    <div className="text-blue-400 font-medium">{opp.token.reply_count}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Age</div>
                    <div className="text-orange-400 font-medium">
                      {Math.floor((Date.now() - opp.token.created_timestamp) / 60000)}m
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-xs text-gray-400 font-mono">
                    {opp.token.mint.slice(0, 8)}...{opp.token.mint.slice(-8)}
                  </div>
                  <button
                    onClick={() => executePumpFunTrade(opp)}
                    disabled={executing === opp.token.mint || !isRunning}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      executing === opp.token.mint
                        ? 'bg-gray-600 cursor-not-allowed'
                        : opp.risk_score <= 4
                          ? 'bg-green-600 hover:bg-green-700'
                          : 'bg-yellow-600 hover:bg-yellow-700'
                    } text-white`}
                  >
                    {executing === opp.token.mint ? '⏳ Sniping...' : '🎯 Snipe'}
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              {isRunning ? (
                <div className="text-gray-400">
                  <svg className="w-8 h-8 mx-auto mb-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <div>Scanning pump.fun for opportunities...</div>
                </div>
              ) : (
                <div className="text-gray-400">
                  <div>Start the bot to begin scanning pump.fun</div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="text-xs text-gray-400 mb-2">Risk Levels:</div>
          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-1"></div>
              <span className="text-gray-400">1-3 (Low Risk)</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mr-1"></div>
              <span className="text-gray-400">4-6 (Medium Risk)</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-red-400 rounded-full mr-1"></div>
              <span className="text-gray-400">7-10 (High Risk)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PumpFunPanel;