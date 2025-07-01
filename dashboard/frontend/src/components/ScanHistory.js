import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  Activity, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Database,
  Calendar,
  TrendingUp
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import axios from 'axios';

const ScanHistory = () => {
  const [limit, setLimit] = useState(20);

  const { data: scanHistory, isLoading, error } = useQuery(
    ['scanHistory', limit],
    () => axios.get(`/dashboard/scan-history?limit=${limit}`).then(res => res.data),
    { refetchInterval: 30000 }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading scan history</h3>
            <p className="text-sm text-red-700 mt-1">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  const totalScans = scanHistory?.length || 0;
  const successfulScans = scanHistory?.reduce((sum, scan) => sum + scan.successful_scans, 0) || 0;
  const totalApisScanned = scanHistory?.reduce((sum, scan) => sum + scan.total_apis_scanned, 0) || 0;
  const successRate = totalApisScanned > 0 ? (successfulScans / totalApisScanned * 100).toFixed(1) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scan History</h1>
          <p className="text-gray-600 mt-2">Monitor automated API scanning activity</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Show:</label>
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={10}>10 scans</option>
              <option value={20}>20 scans</option>
              <option value={50}>50 scans</option>
              <option value={100}>100 scans</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Scans</p>
              <p className="text-2xl font-bold text-gray-900">{totalScans}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Successful Scans</p>
              <p className="text-2xl font-bold text-gray-900">{successfulScans}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Database className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">APIs Scanned</p>
              <p className="text-2xl font-bold text-gray-900">{totalApisScanned}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{successRate}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Scan History Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scan ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  APIs Scanned
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Results
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {scanHistory?.map((scan) => {
                const scanSuccessRate = scan.total_apis_scanned > 0 
                  ? (scan.successful_scans / scan.total_apis_scanned * 100).toFixed(1) 
                  : 0;
                
                return (
                  <tr key={scan.scan_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {scan.scan_id.slice(-8)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {scan.scan_id}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {format(new Date(scan.timestamp * 1000), 'MMM dd, yyyy HH:mm:ss')}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatDistanceToNow(new Date(scan.timestamp * 1000), { addSuffix: true })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {scan.total_apis_scanned} APIs
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className={`h-2 rounded-full ${
                              scanSuccessRate >= 80 ? 'bg-green-500' : 
                              scanSuccessRate >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${scanSuccessRate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">{scanSuccessRate}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="space-y-1">
                        {scan.results?.map((result, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-gray-900">{result.api_name}</span>
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              result.status === 'success' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {result.status === 'success' ? (
                                <CheckCircle className="w-3 h-3 mr-1" />
                              ) : (
                                <AlertTriangle className="w-3 h-3 mr-1" />
                              )}
                              {result.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {scanHistory?.length === 0 && (
          <div className="text-center py-12">
            <Activity className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No scan history</h3>
            <p className="mt-1 text-sm text-gray-500">
              Scan history will appear here once automated scans begin running.
            </p>
          </div>
        )}
      </div>

      {/* Scan Details Modal (if needed) */}
      {scanHistory?.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Scan Activity</h2>
          <div className="space-y-4">
            {scanHistory.slice(0, 3).map((scan) => (
              <div key={scan.scan_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-900">
                    Scan {scan.scan_id.slice(-8)} - {format(new Date(scan.timestamp * 1000), 'MMM dd, yyyy HH:mm')}
                  </h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    scan.successful_scans === scan.total_apis_scanned 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {scan.successful_scans}/{scan.total_apis_scanned} successful
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">APIs Scanned:</span> {scan.total_apis_scanned}
                  </div>
                  <div>
                    <span className="font-medium">Successful:</span> {scan.successful_scans}
                  </div>
                  <div>
                    <span className="font-medium">Failed:</span> {scan.total_apis_scanned - scan.successful_scans}
                  </div>
                  <div>
                    <span className="font-medium">Success Rate:</span> {
                      scan.total_apis_scanned > 0 
                        ? (scan.successful_scans / scan.total_apis_scanned * 100).toFixed(1) 
                        : 0
                    }%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanHistory; 