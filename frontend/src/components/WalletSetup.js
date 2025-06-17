import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WalletSetup = ({ onSetupComplete }) => {
  const [walletAddress, setWalletAddress] = useState('');
  const [rpcEndpoint, setRpcEndpoint] = useState('https://api.mainnet-beta.solana.com');
  const [privateRpcEndpoint, setPrivateRpcEndpoint] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSetup = async (e) => {
    e.preventDefault();
    
    if (!walletAddress.trim()) {
      setError('Wallet address is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const setupData = {
        wallet_address: walletAddress.trim(),
        rpc_endpoint: rpcEndpoint || undefined,
        private_rpc_endpoint: privateRpcEndpoint || undefined
      };

      const response = await axios.post(`${API}/bot/setup`, setupData);
      
      if (response.data.status === 'success') {
        onSetupComplete();
      } else {
        setError('Setup failed: ' + response.data.message);
      }
    } catch (error) {
      setError('Setup failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const generateWallet = () => {
    setError('To generate a new wallet, use the Solana CLI:\n' +
             'solana-keygen new --outfile ~/my-solana-wallet.json\n' +
             'solana-keygen pubkey ~/my-solana-wallet.json');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-gray-800 rounded-lg p-8 shadow-xl">
        <h2 className="text-2xl font-bold text-green-400 mb-6">
          Setup MEV Bot
        </h2>
        
        <form onSubmit={handleSetup} className="space-y-6">
          {/* Wallet Address */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Solana Wallet Address *
            </label>
            <input
              type="text"
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              placeholder="Enter your Solana wallet address"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
            <button
              type="button"
              onClick={generateWallet}
              className="mt-2 text-sm text-blue-400 hover:text-blue-300"
            >
              Need a wallet? Click for instructions
            </button>
          </div>

          {/* RPC Endpoint */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Solana RPC Endpoint
            </label>
            <input
              type="url"
              value={rpcEndpoint}
              onChange={(e) => setRpcEndpoint(e.target.value)}
              placeholder="https://api.mainnet-beta.solana.com"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <p className="mt-1 text-xs text-gray-400">
              Use a premium RPC for better performance
            </p>
          </div>

          {/* Private RPC Endpoint */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Private RPC Endpoint (Optional)
            </label>
            <input
              type="url"
              value={privateRpcEndpoint}
              onChange={(e) => setPrivateRpcEndpoint(e.target.value)}
              placeholder="https://your-private-rpc-endpoint.com"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <p className="mt-1 text-xs text-gray-400">
              Private RPC for faster transaction execution (recommended for MEV)
            </p>
          </div>

          {/* Warning */}
          <div className="bg-yellow-900 border border-yellow-600 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-400">
                  Important Security Notice
                </h3>
                <div className="mt-2 text-sm text-yellow-300">
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Never share your private keys or seed phrases</li>
                    <li>Start with small amounts for testing</li>
                    <li>MEV trading involves significant risks</li>
                    <li>Use dedicated wallets for trading bots</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-900 border border-red-600 rounded-md p-4">
              <pre className="text-sm text-red-300 whitespace-pre-wrap">{error}</pre>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-4 rounded-md font-medium ${
              loading 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-green-600 hover:bg-green-700'
            } text-white transition-colors`}
          >
            {loading ? 'Setting up...' : 'Setup MEV Bot'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default WalletSetup;