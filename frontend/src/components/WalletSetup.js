import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WalletSetup = ({ onSetupComplete }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [walletInfo, setWalletInfo] = useState(null);

  const handleAutoSetup = async () => {
    setLoading(true);
    setError('');

    try {
      // Get wallet info from the configured private key
      const walletResponse = await axios.get(`${API}/bot/wallet-info`);
      
      if (walletResponse.data.status === 'success') {
        setWalletInfo(walletResponse.data);
        
        // Auto-setup the bot with the configured wallet
        const setupData = {
          wallet_address: walletResponse.data.wallet_address,
          rpc_endpoint: "https://syndica.io/access/mainnet/29ujZxresfgVvqqVzeNyjLJShfY1wEnD6NJgRy9fTR3QNXuBDsiwdJdQfbxS6rwTPm2FW79V6HqQsb9KjeMsszRZBpRgS796zrg",
          private_rpc_endpoint: "https://syndica.io/access/mainnet/29ujZxresfgVvqqVzeNyjLJShfY1wEnD6NJgRy9fTR3QNXuBDsiwdJdQfbxS6rwTPm2FW79V6HqQsb9KjeMsszRZBpRgS796zrg"
        };

        const response = await axios.post(`${API}/bot/setup`, setupData);
        
        if (response.data.status === 'success') {
          onSetupComplete();
        } else {
          setError('Setup failed: ' + response.data.message);
        }
      }
    } catch (error) {
      setError('Setup failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-gray-800 rounded-lg p-8 shadow-xl">
        <h2 className="text-3xl font-bold text-green-400 mb-6 text-center">
          🚀 $8 Micro MEV Bot Ready!
        </h2>
        
        {/* Pre-configured Info */}
        <div className="bg-green-900 border border-green-600 rounded-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-green-300 mb-3">
            ✅ Bot Pre-Configured for Profit
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-green-200 font-medium">Strategies Enabled:</div>
              <ul className="text-green-300 ml-4">
                <li>• Raydium AMM/CPMM Arbitrage</li>
                <li>• Meteora DLMM Trading</li>
                <li>• Pump.fun Token Sniping</li>
                <li>• Jupiter Aggregator Routes</li>
              </ul>
            </div>
            <div>
              <div className="text-green-200 font-medium">Safety Features:</div>
              <ul className="text-green-300 ml-4">
                <li>• Max $1 per trade</li>
                <li>• 2% minimum profit required</li>
                <li>• $0.20 daily loss limit</li>
                <li>• Auto gas fee management</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Wallet Status */}
        {walletInfo && (
          <div className="bg-blue-900 border border-blue-600 rounded-md p-6 mb-6">
            <h3 className="text-lg font-semibold text-blue-300 mb-3">
              💰 Wallet Status
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-blue-200 text-sm">Balance</div>
                <div className="text-blue-100 font-bold">${walletInfo.balance_usd.toFixed(2)} USD</div>
                <div className="text-blue-300 text-sm">{walletInfo.balance_sol.toFixed(4)} SOL</div>
              </div>
              <div>
                <div className="text-blue-200 text-sm">Available for Trading</div>
                <div className="text-green-400 font-bold">${(walletInfo.available_for_trading * 200).toFixed(2)}</div>
                <div className="text-blue-300 text-sm">{walletInfo.available_for_trading.toFixed(4)} SOL</div>
              </div>
              <div>
                <div className="text-blue-200 text-sm">Max Trade Size</div>
                <div className="text-orange-400 font-bold">${(walletInfo.max_trade_size * 200).toFixed(2)}</div>
                <div className="text-blue-300 text-sm">{walletInfo.max_trade_size.toFixed(4)} SOL</div>
              </div>
            </div>
          </div>
        )}

        {/* DEX Information */}
        <div className="bg-purple-900 border border-purple-600 rounded-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-purple-300 mb-3">
            🏛️ Connected DEX Platforms
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-purple-200 font-medium">Raydium</div>
              <div className="text-green-400 text-sm">✅ AMM + CPMM</div>
            </div>
            <div className="text-center">
              <div className="text-purple-200 font-medium">Meteora</div>
              <div className="text-green-400 text-sm">✅ DLMM</div>
            </div>
            <div className="text-center">
              <div className="text-purple-200 font-medium">Pump.fun</div>
              <div className="text-green-400 text-sm">✅ Sniping</div>
            </div>
            <div className="text-center">
              <div className="text-purple-200 font-medium">Jupiter</div>
              <div className="text-green-400 text-sm">✅ Routing</div>
            </div>
          </div>
        </div>

        {/* Important Notes */}
        <div className="bg-yellow-900 border border-yellow-600 rounded-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-yellow-300 mb-3">
            ⚡ Optimized for Your $8 Balance
          </h3>
          <div className="text-yellow-200 space-y-2">
            <p>• <strong>Ultra-Conservative:</strong> Max 0.005 SOL ($1) per trade to preserve capital</p>
            <p>• <strong>High Profit Targets:</strong> Minimum 2% profit required (vs typical 0.5%)</p>
            <p>• <strong>Gas Protection:</strong> Reserves 0.005 SOL for transaction fees</p>
            <p>• <strong>24/7 Operation:</strong> Scans every 2 seconds for opportunities</p>
            <p>• <strong>Smart Routing:</strong> Uses Jupiter for best execution prices</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-600 rounded-md p-4 mb-6">
            <div className="text-sm text-red-300">{error}</div>
          </div>
        )}

        <button
          onClick={handleAutoSetup}
          disabled={loading}
          className={`w-full py-4 px-6 rounded-md font-bold text-lg ${
            loading 
              ? 'bg-gray-600 cursor-not-allowed' 
              : 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700'
          } text-white transition-all transform hover:scale-105`}
        >
          {loading ? '🔄 Initializing Bot...' : '🚀 Start MEV Bot & Begin Earning!'}
        </button>

        <div className="mt-4 text-center text-sm text-gray-400">
          Ready to turn your $8 into profit with advanced MEV strategies!
        </div>
      </div>
    </div>
  );
};

export default WalletSetup;