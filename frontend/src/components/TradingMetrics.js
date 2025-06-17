import React from 'react';

const TradingMetrics = ({ status, trades }) => {
  const calculateMetrics = () => {
    if (!status?.session_stats) {
      return {
        totalProfit: 0,
        totalTrades: 0,
        successRate: 0,
        avgProfit: 0,
        winRate: 0,
        bestTrade: 0,
        worstTrade: 0
      };
    }

    const stats = status.session_stats;
    const recentTrades = trades || [];
    
    // Calculate additional metrics from recent trades
    const profitableTrades = recentTrades.filter(trade => 
      trade.profit && trade.profit > 0
    );
    
    const avgProfit = recentTrades.length > 0 
      ? recentTrades.reduce((sum, trade) => sum + (trade.profit || 0), 0) / recentTrades.length
      : 0;

    const profits = recentTrades.map(trade => trade.profit || 0).filter(p => p !== 0);
    const bestTrade = profits.length > 0 ? Math.max(...profits) : 0;
    const worstTrade = profits.length > 0 ? Math.min(...profits) : 0;

    return {
      totalProfit: stats.profit_loss || 0,
      totalTrades: stats.trades_executed || 0,
      successRate: stats.success_rate || 0,
      avgProfit,
      winRate: recentTrades.length > 0 ? (profitableTrades.length / recentTrades.length) * 100 : 0,
      bestTrade,
      worstTrade: worstTrade < 0 ? Math.abs(worstTrade) : 0
    };
  };

  const metrics = calculateMetrics();

  const MetricCard = ({ title, value, suffix = '', color = 'text-white', subValue = null }) => (
    <div className="bg-gray-700 rounded-lg p-4">
      <div className="text-sm text-gray-400 mb-1">{title}</div>
      <div className={`text-2xl font-bold ${color}`}>
        {typeof value === 'number' ? value.toFixed(4) : value}{suffix}
      </div>
      {subValue && (
        <div className="text-xs text-gray-500 mt-1">{subValue}</div>
      )}
    </div>
  );

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <h3 className="text-lg font-semibold text-white mb-4">Trading Metrics</h3>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <MetricCard
          title="Total P&L"
          value={metrics.totalProfit}
          suffix=" SOL"
          color={metrics.totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}
        />
        <MetricCard
          title="Total Trades"
          value={metrics.totalTrades}
          color="text-blue-400"
        />
        <MetricCard
          title="Success Rate"
          value={metrics.successRate}
          suffix="%"
          color={metrics.successRate >= 70 ? 'text-green-400' : metrics.successRate >= 50 ? 'text-yellow-400' : 'text-red-400'}
        />
        <MetricCard
          title="Win Rate"
          value={metrics.winRate}
          suffix="%"
          color={metrics.winRate >= 60 ? 'text-green-400' : 'text-yellow-400'}
        />
      </div>

      <div className="grid grid-cols-1 gap-4">
        <MetricCard
          title="Average Profit per Trade"
          value={metrics.avgProfit}
          suffix=" SOL"
          color={metrics.avgProfit >= 0 ? 'text-green-400' : 'text-red-400'}
        />
        
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            title="Best Trade"
            value={metrics.bestTrade}
            suffix=" SOL"
            color="text-green-400"
          />
          <MetricCard
            title="Worst Loss"
            value={metrics.worstTrade}
            suffix=" SOL"
            color="text-red-400"
          />
        </div>
      </div>

      {/* Performance Indicators */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="text-sm text-gray-400 mb-2">Performance Indicators</div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Profitability</span>
            <div className={`text-xs px-2 py-1 rounded-full ${
              metrics.totalProfit > 0 
                ? 'bg-green-900 text-green-300' 
                : metrics.totalProfit < 0 
                  ? 'bg-red-900 text-red-300'
                  : 'bg-gray-700 text-gray-300'
            }`}>
              {metrics.totalProfit > 0 ? 'Profitable' : metrics.totalProfit < 0 ? 'Losing' : 'Break Even'}
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Trading Activity</span>
            <div className={`text-xs px-2 py-1 rounded-full ${
              status?.is_running 
                ? 'bg-green-900 text-green-300' 
                : 'bg-red-900 text-red-300'
            }`}>
              {status?.is_running ? 'Active' : 'Inactive'}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Risk Level</span>
            <div className={`text-xs px-2 py-1 rounded-full ${
              metrics.successRate >= 70 
                ? 'bg-green-900 text-green-300' 
                : metrics.successRate >= 50 
                  ? 'bg-yellow-900 text-yellow-300'
                  : 'bg-red-900 text-red-300'
            }`}>
              {metrics.successRate >= 70 ? 'Low' : metrics.successRate >= 50 ? 'Medium' : 'High'}
            </div>
          </div>
        </div>
      </div>

      {/* Session Info */}
      {status?.session_stats?.start_time && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="text-xs text-gray-400">
            Session started: {new Date(status.session_stats.start_time).toLocaleString()}
          </div>
          <div className="text-xs text-gray-400">
            Scans performed: {status.session_stats.total_scans || 0}
          </div>
          <div className="text-xs text-gray-400">
            Opportunities found: {status.session_stats.opportunities_found || 0}
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingMetrics;