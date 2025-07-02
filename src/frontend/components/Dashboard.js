import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  RefreshCw,
  TrendingUp,
  Database,
  Eye
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import axios from 'axios';

const Dashboard = () => {
  const { data: apiSummary, isLoading: summaryLoading } = useQuery(
    'apiSummary',
    () => axios.get('/dashboard/api-summary').then(res => res.data),
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const { data: scanHistory, isLoading: historyLoading } = useQuery(
    'scanHistory',
    () => axios.get('/dashboard/scan-history?limit=5').then(res => res.data),
    { refetchInterval: 30000 }
  );

  const { data: listApis } = useQuery(
    'listApis',
    () => axios.get('/list-apis').then(res => res.data),
    { refetchInterval: 30000 }
  );

  if (summaryLoading || historyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const totalApis = apiSummary?.length || 0;
  const totalEndpoints = apiSummary?.reduce((sum, api) => sum + api.total_endpoints, 0) || 0;
  const apisWithChanges = apiSummary?.filter(api => 
    api.recent_changes.added > 0 || 
    api.recent_changes.removed > 0 || 
    api.recent_changes.modified > 0
  ).length || 0;
  const lastScan = scanHistory?.[0]?.timestamp;

  const recentChanges = apiSummary?.filter(api => 
    api.last_change_timestamp && 
    (Date.now() / 1000 - api.last_change_timestamp) < 86400 // Last 24 hours
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">NL2Flow Dashboard</h1>
          <p className="text-gray-600 mt-2">Monitor API changes and scan history</p>
        </div>
        <div className="flex space-x-3">
          <Link
            to="/api-summary"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Eye className="inline w-4 h-4 mr-2" />
            View All APIs
          </Link>
          <Link
            to="/scan-history"
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <Activity className="inline w-4 h-4 mr-2" />
            Scan History
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total APIs</p>
              <p className="text-2xl font-bold text-gray-900">{totalApis}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Endpoints</p>
              <p className="text-2xl font-bold text-gray-900">{totalEndpoints}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">APIs with Changes</p>
              <p className="text-2xl font-bold text-gray-900">{apisWithChanges}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Last Scan</p>
              <p className="text-lg font-bold text-gray-900">
                {lastScan ? formatDistanceToNow(new Date(lastScan * 1000), { addSuffix: true }) : 'Never'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Changes */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Changes</h2>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          
          {recentChanges.length > 0 ? (
            <div className="space-y-3">
              {recentChanges.slice(0, 5).map((api) => (
                <div key={api.api_name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{api.api_name}</p>
                    <p className="text-sm text-gray-600">
                      {api.recent_changes.added} added, {api.recent_changes.removed} removed, {api.recent_changes.modified} modified
                    </p>
                  </div>
                  <Link
                    to={`/api-changes/${api.api_name}`}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Details
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No recent changes detected</p>
          )}
        </div>

        {/* Recent Scans */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Scans</h2>
            <RefreshCw className="w-5 h-5 text-gray-400" />
          </div>
          
          {scanHistory && scanHistory.length > 0 ? (
            <div className="space-y-3">
              {scanHistory.slice(0, 5).map((scan) => (
                <div key={scan.scan_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">
                      Scan {scan.scan_id.slice(-8)}
                    </p>
                    <p className="text-sm text-gray-600">
                      {scan.successful_scans}/{scan.total_apis_scanned} successful
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(scan.timestamp * 1000), { addSuffix: true })}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      scan.successful_scans === scan.total_apis_scanned 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {scan.successful_scans === scan.total_apis_scanned ? 'Success' : 'Partial'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No scan history available</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors">
            <RefreshCw className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-gray-600">Trigger Manual Scan</span>
          </button>
          <Link
            to="/api-summary"
            className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-400 hover:bg-green-50 transition-colors"
          >
            <Database className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-gray-600">View API Details</span>
          </Link>
          <Link
            to="/scan-history"
            className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-colors"
          >
            <Activity className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-gray-600">View Scan History</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 