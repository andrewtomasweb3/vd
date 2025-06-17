import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BotControls = ({ botStatus, onStatusChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStart = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/bot/start`);
      if (response.data.status === 'success' || response.data.status === 'already_running') {
        onStatusChange();
      } else {
        setError('Failed to start bot: ' + response.data.message);
      }
    } catch (error) {
      setError('Failed to start bot: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/bot/stop`);
      if (response.data.status === 'success' || response.data.status === 'already_stopped') {
        onStatusChange();
      } else {
        setError('Failed to stop bot: ' + response.data.message);
      }
    } catch (error) {
      setError('Failed to stop bot: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEmergencyStop = async () => {
    if (!window.confirm('Are you sure you want to execute an emergency stop? This will immediately close all positions and stop the bot.')) {
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/bot/emergency-stop`);
      if (response.data.status === 'success') {
        onStatusChange();
        alert('Emergency stop executed successfully!');
      } else {
        setError('Emergency stop failed: ' + response.data.message);
      }
    } catch (error) {
      setError('Emergency stop failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <h3 className="text-lg font-semibold text-white mb-4">Bot Controls</h3>
      
      <div className="space-y-3">
        {/* Start/Stop Button */}
        {botStatus?.is_running ? (
          <button
            onClick={handleStop}
            disabled={loading}
            className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
              loading 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-red-600 hover:bg-red-700'
            } text-white`}
          >
            {loading ? 'Stopping...' : 'Stop Bot'}
          </button>
        ) : (
          <button
            onClick={handleStart}
            disabled={loading}
            className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
              loading 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-green-600 hover:bg-green-700'
            } text-white`}
          >
            {loading ? 'Starting...' : 'Start Bot'}
          </button>
        )}

        {/* Emergency Stop */}
        <button
          onClick={handleEmergencyStop}
          disabled={loading}
          className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
            loading 
              ? 'bg-gray-600 cursor-not-allowed' 
              : 'bg-red-800 hover:bg-red-900 border border-red-600'
          } text-white`}
        >
          🚨 Emergency Stop
        </button>

        {/* Strategy Status */}
        {botStatus?.config?.enabled_strategies && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="text-sm text-gray-300 mb-2">Active Strategies:</div>
            <div className="flex flex-wrap gap-2">
              {botStatus.config.enabled_strategies.map((strategy) => (
                <span
                  key={strategy}
                  className="px-2 py-1 bg-blue-900 text-blue-200 rounded-full text-xs font-medium"
                >
                  {strategy.replace('_', ' ').toUpperCase()}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Configuration Info */}
        {botStatus?.config && (
          <div className="mt-4 pt-4 border-t border-gray-700 text-xs text-gray-400 space-y-1">
            <div>Scan Interval: {botStatus.config.scan_interval}s</div>
            <div>Max Concurrent Trades: {botStatus.config.max_concurrent_trades}</div>
            <div>Min Profit: {botStatus.config.min_profit_percentage}%</div>
            <div>Max Position: {botStatus.config.max_position_size} SOL</div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-900 border border-red-600 rounded-md">
          <div className="text-sm text-red-300">{error}</div>
        </div>
      )}
    </div>
  );
};

export default BotControls;