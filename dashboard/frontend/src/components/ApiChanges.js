import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { 
  ArrowLeft, 
  Plus, 
  Minus, 
  Edit3, 
  Clock, 
  Database,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import axios from 'axios';

const ApiChanges = () => {
  const { apiName } = useParams();

  const { data: apiChanges, isLoading, error } = useQuery(
    ['apiChanges', apiName],
    () => axios.get(`/dashboard/api-changes/${apiName}?limit=50`).then(res => res.data),
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
            <h3 className="text-sm font-medium text-red-800">Error loading API changes</h3>
            <p className="text-sm text-red-700 mt-1">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  const totalScans = apiChanges?.total_scans || 0;
  const totalEndpoints = apiChanges?.scans?.[0]?.endpoints_count || 0;
  const firstScan = apiChanges?.scans?.[apiChanges.scans.length - 1];
  const lastScan = apiChanges?.scans?.[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/api-summary"
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{apiName}</h1>
            <p className="text-gray-600 mt-2">API change history and monitoring</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Database className="w-6 h-6 text-blue-600" />
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
              <Plus className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Current Endpoints</p>
              <p className="text-2xl font-bold text-gray-900">{totalEndpoints}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">First Scan</p>
              <p className="text-lg font-bold text-gray-900">
                {firstScan ? formatDistanceToNow(new Date(firstScan.timestamp * 1000), { addSuffix: true }) : 'Never'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Last Scan</p>
              <p className="text-lg font-bold text-gray-900">
                {lastScan ? formatDistanceToNow(new Date(lastScan.timestamp * 1000), { addSuffix: true }) : 'Never'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Scan History */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Scan History</h2>
          <p className="text-sm text-gray-600 mt-1">
            Detailed history of all scans for this API
          </p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scan Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Endpoints
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Changes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {apiChanges?.scans?.map((scan, index) => {
                const previousScan = apiChanges.scans[index + 1];
                let changes = { added: 0, removed: 0, modified: 0 };
                
                if (previousScan) {
                  const currentEndpoints = new Set(
                    scan.endpoints.map(e => `${e.method} ${e.endpoint}`)
                  );
                  const previousEndpoints = new Set(
                    previousScan.endpoints.map(e => `${e.method} ${e.endpoint}`)
                  );
                  
                  changes.added = [...currentEndpoints].filter(e => !previousEndpoints.has(e)).length;
                  changes.removed = [...previousEndpoints].filter(e => !currentEndpoints.has(e)).length;
                  // Modified would require deeper comparison of schemas
                }
                
                return (
                  <tr key={scan.timestamp} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {format(new Date(scan.timestamp * 1000), 'MMM dd, yyyy HH:mm:ss')}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatDistanceToNow(new Date(scan.timestamp * 1000), { addSuffix: true })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {scan.endpoints_count} endpoints
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex space-x-2">
                        {changes.added > 0 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <Plus className="w-3 h-3 mr-1" />
                            +{changes.added}
                          </span>
                        )}
                        {changes.removed > 0 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <Minus className="w-3 h-3 mr-1" />
                            -{changes.removed}
                          </span>
                        )}
                        {changes.modified > 0 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <Edit3 className="w-3 h-3 mr-1" />
                            ~{changes.modified}
                          </span>
                        )}
                        {changes.added === 0 && changes.removed === 0 && changes.modified === 0 && (
                          <span className="text-xs text-gray-500">No changes</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-blue-600 hover:text-blue-900">
                        View Details
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {apiChanges?.scans?.length === 0 && (
          <div className="text-center py-12">
            <Database className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No scan history</h3>
            <p className="mt-1 text-sm text-gray-500">
              This API hasn't been scanned yet.
            </p>
          </div>
        )}
      </div>

      {/* Endpoint Details (Latest Scan) */}
      {lastScan && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Current Endpoints</h2>
            <p className="text-sm text-gray-600 mt-1">
              Latest scan from {format(new Date(lastScan.timestamp * 1000), 'MMM dd, yyyy HH:mm')}
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Method
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Endpoint
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Auth Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Schema
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {lastScan.endpoints?.map((endpoint, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        endpoint.method === 'GET' ? 'bg-green-100 text-green-800' :
                        endpoint.method === 'POST' ? 'bg-blue-100 text-blue-800' :
                        endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' :
                        endpoint.method === 'DELETE' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {endpoint.method}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 font-mono">
                        {endpoint.endpoint}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {endpoint.metadata?.auth_type || 'none'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        <div>Input: {endpoint.schema?.input?.type || 'none'}</div>
                        <div>Output: {endpoint.schema?.output?.type || 'none'}</div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiChanges; 