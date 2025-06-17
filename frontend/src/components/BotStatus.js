import React from 'react';

const BotStatus = ({ status, walletBalance, onRefresh }) => {
  if (!status) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-300 mb-4">Bot Status</h3>
        <div className="text-center py-8">
          <div className="animate-pulse text-gray-400">Loading...</div>
        </div>
      </div>
    );
  }

  const getStatusColor = () => {
    if (status.is_running) return 'text-green-400';
    return 'text-red-400';
  };

  const getStatusBadge = () => {
    if (status.is_running) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <span className="w-2 h-2 bg-green-400 rounded-full mr-1 animate-pulse"></span>
          Running
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        <span className="w-2 h-2 bg-red-400 rounded-full mr-1"></span>
        Stopped
      </span>
    );
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Bot Status</h3>
        <button
          onClick={onRefresh}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <div className="space-y-4">
        {/* Status Badge */}
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Status:</span>
          {getStatusBadge()}
        </div>

        {/* Wallet Address */}
        <div>
          <span className="text-gray-300">Wallet:</span>
          <div className="text-sm text-blue-400 font-mono mt-1">
            {status.wallet_address ? 
              `${status.wallet_address.slice(0, 8)}...${status.wallet_address.slice(-8)}` : 
              'Not configured'
            }
          </div>
        </div>

        {/* Wallet Balance */}
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Balance:</span>
          <span className="text-green-400 font-semibold">
            {status.wallet_balance ? `${status.wallet_balance.toFixed(4)} SOL` : '-.---- SOL'}
          </span>
        </div>

        {/* Current Opportunities */}
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Opportunities:</span>
          <span className="text-yellow-400 font-semibold">
            {status.current_opportunities || 0}
          </span>
        </div>

        {/* Active Positions */}
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Active Positions:</span>
          <span className="text-blue-400 font-semibold">
            {status.active_positions || 0}
          </span>
        </div>

        {/* Session Profit/Loss */}
        {status.session_stats && (
          <div className="pt-4 border-t border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Session P&L:</span>
              <span className={`font-semibold ${
                status.session_stats.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {status.session_stats.profit_loss >= 0 ? '+' : ''}
                {status.session_stats.profit_loss.toFixed(4)} SOL
              </span>
            </div>
            
            <div className="flex items-center justify-between mt-2">
              <span className="text-gray-300">Success Rate:</span>
              <span className="text-blue-400 font-semibold">
                {status.session_stats.success_rate?.toFixed(1) || 0}%
              </span>
            </div>
          </div>
        )}

        {/* Runtime */}
        {status.is_running && status.session_stats?.start_time && (
          <div className="text-xs text-gray-400">
            Running since: {new Date(status.session_stats.start_time).toLocaleString()}
          </div>
        )}
      </div>
    </div>
  );
};

export default BotStatus;