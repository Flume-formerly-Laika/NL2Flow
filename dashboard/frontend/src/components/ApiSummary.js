import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Plus,
  Search,
  Filter
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import axios from 'axios';

const ApiSummary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [rescanModal, setRescanModal] = useState({ show: false, api: null });
  const [rescanForm, setRescanForm] = useState({ api_name: '', openapi_url: '' });

  const queryClient = useQueryClient();

  const { data: apiSummary, isLoading, error } = useQuery(
    'apiSummary',
    () => axios.get('/dashboard/api-summary').then(res => res.data),
    { refetchInterval: 30000 }
  );

  const rescanMutation = useMutation(
    (data) => axios.post('/dashboard/rescan-api', data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('apiSummary');
        setRescanModal({ show: false, api: null });
        setRescanForm({ api_name: '', openapi_url: '' });
      },
    }
  );

  const handleRescan = (api) => {
    setRescanModal({ show: true, api });
    setRescanForm({ 
      api_name: api.api_name, 
      openapi_url: '' 
    });
  };

  const submitRescan = () => {
    if (rescanForm.api_name && rescanForm.openapi_url) {
      rescanMutation.mutate(rescanForm);
    }
  };

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
            <h3 className="text-sm font-medium text-red-800">Error loading API summary</h3>
            <p className="text-sm text-red-700 mt-1">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  // Filter APIs based on search and status
  const filteredApis = apiSummary?.filter(api => {
    const matchesSearch = api.api_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || 
      (filterStatus === 'changed' && (
        api.recent_changes.added > 0 || 
        api.recent_changes.removed > 0 || 
        api.recent_changes.modified > 0
      )) ||
      (filterStatus === 'stable' && (
        api.recent_changes.added === 0 && 
        api.recent_changes.removed === 0 && 
        api.recent_changes.modified === 0
      ));
    
    return matchesSearch && matchesStatus;
  }) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">API Summary</h1>
          <p className="text-gray-600 mt-2">Monitor all APIs and their recent changes</p>
        </div>
        <button
          onClick={() => setRescanModal({ show: true, api: null })}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add New API
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search APIs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All APIs</option>
              <option value="changed">With Changes</option>
              <option value="stable">Stable</option>
            </select>
          </div>
        </div>
      </div>

      {/* API List */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  API Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Endpoints
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recent Changes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Scan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredApis.map((api) => (
                <tr key={api.api_name} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{api.api_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      api.last_scan_status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {api.last_scan_status === 'success' ? (
                        <CheckCircle className="w-3 h-3 mr-1" />
                      ) : (
                        <AlertTriangle className="w-3 h-3 mr-1" />
                      )}
                      {api.last_scan_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {api.total_endpoints}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex space-x-2">
                      {api.recent_changes.added > 0 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          +{api.recent_changes.added}
                        </span>
                      )}
                      {api.recent_changes.removed > 0 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          -{api.recent_changes.removed}
                        </span>
                      )}
                      {api.recent_changes.modified > 0 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          ~{api.recent_changes.modified}
                        </span>
                      )}
                      {api.recent_changes.added === 0 && api.recent_changes.removed === 0 && api.recent_changes.modified === 0 && (
                        <span className="text-xs text-gray-500">No changes</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDistanceToNow(new Date(api.last_scan_timestamp * 1000), { addSuffix: true })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <Link
                        to={`/api-changes/${api.api_name}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View
                      </Link>
                      <button
                        onClick={() => handleRescan(api)}
                        className="text-green-600 hover:text-green-900 flex items-center"
                      >
                        <RefreshCw className="w-3 h-3 mr-1" />
                        Rescan
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredApis.length === 0 && (
          <div className="text-center py-12">
            <Database className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No APIs found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || filterStatus !== 'all' 
                ? 'Try adjusting your search or filter criteria.' 
                : 'Get started by adding your first API.'}
            </p>
          </div>
        )}
      </div>

      {/* Rescan Modal */}
      {rescanModal.show && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {rescanModal.api ? 'Rescan API' : 'Add New API'}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">API Name</label>
                  <input
                    type="text"
                    value={rescanForm.api_name}
                    onChange={(e) => setRescanForm({ ...rescanForm, api_name: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., PetStore"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">OpenAPI URL</label>
                  <input
                    type="url"
                    value={rescanForm.openapi_url}
                    onChange={(e) => setRescanForm({ ...rescanForm, openapi_url: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="https://petstore.swagger.io/v2/swagger.json"
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setRescanModal({ show: false, api: null })}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={submitRescan}
                  disabled={!rescanForm.api_name || !rescanForm.openapi_url || rescanMutation.isLoading}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {rescanMutation.isLoading ? 'Scanning...' : (rescanModal.api ? 'Rescan' : 'Add API')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiSummary; 