import React from 'react';

const OpportunitiesPanel = ({ opportunities, isRunning }) => {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getOpportunityColor = (profitPercentage) => {
    if (profitPercentage >= 2.0) return 'text-green-300';
    if (profitPercentage >= 1.0) return 'text-green-400';
    if (profitPercentage >= 0.5) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const OpportunityCard = ({ opportunity }) => (
    <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-white">{opportunity.token_symbol}</span>
          <span className="text-xs text-gray-400 font-mono">
            {opportunity.token_mint.slice(0, 8)}...
          </span>
        </div>
        <span className={`font-bold ${getOpportunityColor(opportunity.profit_percentage)}`}>
          +{opportunity.profit_percentage.toFixed(2)}%
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-gray-400">Buy on</div>
          <div className="text-blue-400 font-medium">{opportunity.buy_dex}</div>
          <div className="text-gray-300">${opportunity.buy_price.toFixed(6)}</div>
        </div>
        <div>
          <div className="text-gray-400">Sell on</div>
          <div className="text-green-400 font-medium">{opportunity.sell_dex}</div>
          <div className="text-gray-300">${opportunity.sell_price.toFixed(6)}</div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-600">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">
            Potential: {opportunity.profit_amount.toFixed(4)} SOL
          </span>
          <span className="text-gray-400">
            {formatTimestamp(opportunity.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Arbitrage Opportunities</h3>
        <div className="flex items-center space-x-2">
          {isRunning && (
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
              <span className="text-xs text-green-400">Scanning</span>
            </div>
          )}
          <span className="text-sm text-gray-400">
            {opportunities.length} found
          </span>
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {opportunities.length > 0 ? (
          opportunities.map((opportunity, index) => (
            <OpportunityCard key={index} opportunity={opportunity} />
          ))
        ) : (
          <div className="text-center py-8">
            {isRunning ? (
              <div className="text-gray-400">
                <svg className="w-8 h-8 mx-auto mb-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <div>Scanning for opportunities...</div>
              </div>
            ) : (
              <div className="text-gray-400">
                <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <div>No opportunities found</div>
                <div className="text-xs text-gray-500 mt-1">
                  Start the bot to begin scanning
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="text-xs text-gray-400 mb-2">Profit Levels:</div>
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-300 rounded-full mr-1"></div>
            <span className="text-gray-400">2%+ (Excellent)</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-1"></div>
            <span className="text-gray-400">1-2% (Good)</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-yellow-400 rounded-full mr-1"></div>
            <span className="text-gray-400">0.5-1% (Fair)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpportunitiesPanel;