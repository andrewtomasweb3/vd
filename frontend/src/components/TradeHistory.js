import React from 'react';

const TradeHistory = ({ trades, onRefresh }) => {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getTradeTypeColor = (type) => {
    switch (type) {
      case 'arbitrage': return 'bg-blue-900 text-blue-300';
      case 'token_snipe': return 'bg-purple-900 text-purple-300';
      case 'sandwich': return 'bg-green-900 text-green-300';
      case 'emergency_stop': return 'bg-red-900 text-red-300';
      default: return 'bg-gray-900 text-gray-300';
    }
  };

  const getTradeTypeIcon = (type) => {
    switch (type) {
      case 'arbitrage':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        );
      case 'token_snipe':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
      case 'sandwich':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        );
    }
  };

  const TradeCard = ({ trade }) => (
    <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getTradeTypeColor(trade.type)}`}>
            {getTradeTypeIcon(trade.type)}
            <span>{trade.type.replace('_', ' ').toUpperCase()}</span>
          </span>
          <span className="font-semibold text-white">{trade.token}</span>
        </div>
        {trade.profit && (
          <span className={`font-bold ${trade.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trade.profit >= 0 ? '+' : ''}{trade.profit.toFixed(4)} SOL
          </span>
        )}
      </div>

      {/* Trade Details */}
      {trade.details && (
        <div className="text-sm text-gray-300 space-y-1">
          {trade.details.buy_dex && trade.details.sell_dex && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Route:</span>
              <span>{trade.details.buy_dex} → {trade.details.sell_dex}</span>
            </div>
          )}
          
          {trade.details.profit_percentage && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Profit %:</span>
              <span className="text-green-400">+{trade.details.profit_percentage.toFixed(2)}%</span>
            </div>
          )}

          {trade.details.buy_price && trade.details.sell_price && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Buy: ${trade.details.buy_price.toFixed(6)}</span>
              <span className="text-gray-400">Sell: ${trade.details.sell_price.toFixed(6)}</span>
            </div>
          )}

          {trade.details.risk_score && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Risk:</span>
              <span className={`${trade.details.risk_score <= 3 ? 'text-green-400' : trade.details.risk_score <= 6 ? 'text-yellow-400' : 'text-red-400'}`}>
                {trade.details.risk_score}/10
              </span>
            </div>
          )}
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-gray-600">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>ID: {trade.id.slice(0, 8)}...</span>
          <span>{formatTimestamp(trade.timestamp)}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Trade History</h3>
        <button
          onClick={onRefresh}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {trades.length > 0 ? (
          trades.map((trade, index) => (
            <TradeCard key={trade.id || index} trade={trade} />
          ))
        ) : (
          <div className="text-center py-8">
            <svg className="w-8 h-8 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <div className="text-gray-400">No trades yet</div>
            <div className="text-xs text-gray-500 mt-1">
              Trades will appear here once the bot starts executing
            </div>
          </div>
        )}
      </div>

      {/* Trade Summary */}
      {trades.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-xs text-gray-400">Total Trades</div>
              <div className="text-sm font-semibold text-white">{trades.length}</div>
            </div>
            <div>
              <div className="text-xs text-gray-400">Profitable</div>
              <div className="text-sm font-semibold text-green-400">
                {trades.filter(t => t.profit > 0).length}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-400">Losses</div>
              <div className="text-sm font-semibold text-red-400">
                {trades.filter(t => t.profit < 0).length}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradeHistory;