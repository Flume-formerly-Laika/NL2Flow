/**
 * @file Dashboard.js
 * @brief Main dashboard component for NL2Flow admin interface
 * @author Huy Le (huyisme-005)
 * @description 
 *     Main dashboard view that displays API scan results, schema changes,
 *     and provides manual rescan functionality. Integrates with the FastAPI
 *     backend to fetch data and trigger rescans.
 * 
 *     Key Features:
 *     - Display API scan history and status
 *     - Show schema change notifications
 *     - Manual rescan functionality
 *     - Real-time data updates
 *     - Responsive design with Tailwind CSS
 * 
 *     Component Structure:
 *     - API Summary Table
 *     - Scan History Timeline
 *     - Change Detection Alerts
 *     - Manual Rescan Controls
 * 
 *     Potential Issues:
 *     - API connection failures
 *     - Large data sets causing performance issues
 *     - Real-time updates not working
 *     - CORS issues with backend
 * 
 *     Debugging Tips:
 *     - Check browser console for API errors
 *     - Verify backend URL configuration
 *     - Monitor network requests in DevTools
 *     - Check CORS headers on backend
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
    RefreshCw, 
    AlertTriangle, 
    CheckCircle, 
    Clock, 
    Eye,
    Play,
    Loader2
} from 'lucide-react';

const Dashboard = () => {
    const [apiSummary, setApiSummary] = useState([]);
    const [scanHistory, setScanHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedApi, setSelectedApi] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    const [rescanLoading, setRescanLoading] = useState({});

    // API base URL - should be configured via environment variables
    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

    /**
     * @function fetchApiSummary
     * @brief Fetch API summary data from backend
     * @description Retrieves current API scan status and recent changes
     */
    const fetchApiSummary = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/api-summary`);
            setApiSummary(response.data);
        } catch (err) {
            console.error('Error fetching API summary:', err);
            setError('Failed to load API summary');
        }
    };

    /**
     * @function fetchScanHistory
     * @brief Fetch scan history from backend
     * @description Retrieves recent scan execution history
     */
    const fetchScanHistory = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/scan-history?limit=10`);
            setScanHistory(response.data);
        } catch (err) {
            console.error('Error fetching scan history:', err);
            setError('Failed to load scan history');
        }
    };

    /**
     * @function handleRescan
     * @brief Trigger manual rescan for specific API
     * @param apiName Name of the API to rescan
     * @param openapiUrl OpenAPI specification URL
     * @description Initiates a manual rescan and updates the UI accordingly
     */
    const handleRescan = async (apiName, openapiUrl) => {
        setRescanLoading(prev => ({ ...prev, [apiName]: true }));
        
        try {
            const response = await axios.post(`${API_BASE_URL}/dashboard/rescan-api`, {
                api_name: apiName,
                openapi_url: openapiUrl
            });

            // Show success notification
            alert(`Rescan completed for ${apiName}. Changes detected: ${response.data.changes_detected ? 'Yes' : 'No'}`);
            
            // Refresh data
            await fetchApiSummary();
            await fetchScanHistory();
            
        } catch (err) {
            console.error('Error during rescan:', err);
            alert(`Rescan failed for ${apiName}: ${err.response?.data?.detail || err.message}`);
        } finally {
            setRescanLoading(prev => ({ ...prev, [apiName]: false }));
        }
    };

    /**
     * @function handleApiClick
     * @brief Handle API row click to show details
     * @param api API data object
     * @description Shows detailed view for selected API
     */
    const handleApiClick = async (api) => {
        setSelectedApi(api);
        setShowDetails(true);
        
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/api-changes/${api.api_name}?limit=5`);
            setSelectedApi(prev => ({ ...prev, changes: response.data }));
        } catch (err) {
            console.error('Error fetching API changes:', err);
        }
    };

    /**
     * @function formatTimestamp
     * @brief Format timestamp for display
     * @param timestamp Unix timestamp
     * @return Formatted date string
     */
    const formatTimestamp = (timestamp) => {
        return new Date(timestamp * 1000).toLocaleString();
    };

    /**
     * @function getStatusIcon
     * @brief Get appropriate icon for API status
     * @param status API status string
     * @return React component
     */
    const getStatusIcon = (status) => {
        switch (status) {
            case 'success':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case 'error':
                return <AlertTriangle className="w-4 h-4 text-red-500" />;
            default:
                return <Clock className="w-4 h-4 text-yellow-500" />;
        }
    };

    /**
     * @function getChangeIndicator
     * @brief Get change detection indicator
     * @param changes Recent changes object
     * @return React component
     */
    const getChangeIndicator = (changes) => {
        if (!changes) return <span className="text-gray-400">-</span>;
        
        const hasChanges = Object.values(changes).some(count => count > 0);
        
        return hasChanges ? (
            <span className="flex items-center text-green-600">
                <CheckCircle className="w-4 h-4 mr-1" />
                Yes
            </span>
        ) : (
            <span className="flex items-center text-gray-500">
                <span className="w-4 h-4 mr-1">❌</span>
                No
            </span>
        );
    };

    // Load data on component mount
    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                await Promise.all([fetchApiSummary(), fetchScanHistory()]);
            } catch (err) {
                setError('Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        loadData();

        // Set up auto-refresh every 30 seconds
        const interval = setInterval(loadData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                <span className="ml-2 text-lg">Loading dashboard...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading Dashboard</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button 
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        NL2Flow API Watchdog Dashboard
                    </h1>
                    <p className="text-gray-600">
                        Monitor API schema changes and manage automated scans
                    </p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-lg shadow">
                        <div className="flex items-center">
                            <div className="p-2 bg-blue-100 rounded-lg">
                                <RefreshCw className="w-6 h-6 text-blue-600" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Total APIs</p>
                                <p className="text-2xl font-semibold text-gray-900">{apiSummary.length}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow">
                        <div className="flex items-center">
                            <div className="p-2 bg-green-100 rounded-lg">
                                <CheckCircle className="w-6 h-6 text-green-600" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Successful Scans</p>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {apiSummary.filter(api => api.last_scan_status === 'success').length}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow">
                        <div className="flex items-center">
                            <div className="p-2 bg-yellow-100 rounded-lg">
                                <AlertTriangle className="w-6 h-6 text-yellow-600" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Changes Detected</p>
                                <p className="text-2xl font-semibold text-gray-900">
                                    {apiSummary.filter(api => 
                                        api.recent_changes && 
                                        Object.values(api.recent_changes).some(count => count > 0)
                                    ).length}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow">
                        <div className="flex items-center">
                            <div className="p-2 bg-purple-100 rounded-lg">
                                <Clock className="w-6 h-6 text-purple-600" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Last Scan</p>
                                <p className="text-sm font-semibold text-gray-900">
                                    {apiSummary.length > 0 ? 
                                        formatTimestamp(Math.max(...apiSummary.map(api => api.last_scan_timestamp))) :
                                        'Never'
                                    }
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* API Summary Table */}
                <div className="bg-white rounded-lg shadow mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-xl font-semibold text-gray-900">API Summary</h2>
                        <p className="text-sm text-gray-600 mt-1">
                            Click on any row to view detailed changes
                        </p>
                    </div>
                    
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        API Name
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Last Scan
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Status
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Endpoints
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Changes Detected
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {apiSummary.map((api) => (
                                    <tr 
                                        key={api.api_name}
                                        className="hover:bg-gray-50 cursor-pointer"
                                        onClick={() => handleApiClick(api)}
                                    >
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {api.api_name}
                                                </div>
                                                <Eye className="w-4 h-4 text-gray-400 ml-2" />
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {formatTimestamp(api.last_scan_timestamp)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                {getStatusIcon(api.last_scan_status)}
                                                <span className="ml-2 text-sm text-gray-900 capitalize">
                                                    {api.last_scan_status}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {api.total_endpoints}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {getChangeIndicator(api.recent_changes)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleRescan(api.api_name, `https://api.${api.api_name.toLowerCase()}.com/openapi.json`);
                                                }}
                                                disabled={rescanLoading[api.api_name]}
                                                className="flex items-center px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                                            >
                                                {rescanLoading[api.api_name] ? (
                                                    <Loader2 className="w-4 h-4 animate-spin mr-1" />
                                                ) : (
                                                    <Play className="w-4 h-4 mr-1" />
                                                )}
                                                Rescan
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Scan History */}
                <div className="bg-white rounded-lg shadow">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-xl font-semibold text-gray-900">Recent Scan History</h2>
                    </div>
                    
                    <div className="p-6">
                        {scanHistory.length === 0 ? (
                            <p className="text-gray-500 text-center py-4">No scan history available</p>
                        ) : (
                            <div className="space-y-4">
                                {scanHistory.map((scan) => (
                                    <div key={scan.scan_id} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="font-medium text-gray-900">
                                                    Scan {scan.scan_id}
                                                </h3>
                                                <p className="text-sm text-gray-500">
                                                    {formatTimestamp(scan.timestamp)}
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm text-gray-600">
                                                    {scan.successful_scans}/{scan.total_apis_scanned} successful
                                                </p>
                                                <p className="text-xs text-gray-500">
                                                    {scan.results?.length || 0} APIs scanned
                                                </p>
                                            </div>
                                        </div>
                                        
                                        {scan.results && scan.results.length > 0 && (
                                            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                                                {scan.results.map((result) => (
                                                    <div key={result.api_name} className="text-xs">
                                                        <span className="font-medium">{result.api_name}:</span>
                                                        <span className={`ml-1 ${
                                                            result.status === 'success' ? 'text-green-600' : 'text-red-600'
                                                        }`}>
                                                            {result.status}
                                                        </span>
                                                        {result.endpoints_count > 0 && (
                                                            <span className="text-gray-500 ml-1">
                                                                ({result.endpoints_count} endpoints)
                                                            </span>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* API Details Modal */}
            {showDetails && selectedApi && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <div className="flex justify-between items-center">
                                <h2 className="text-xl font-semibold text-gray-900">
                                    {selectedApi.api_name} - Change Details
                                </h2>
                                <button
                                    onClick={() => setShowDetails(false)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    ✕
                                </button>
                            </div>
                        </div>
                        
                        <div className="p-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-3">Recent Changes</h3>
                                    {selectedApi.recent_changes ? (
                                        <div className="space-y-2">
                                            <div className="flex justify-between">
                                                <span>Added:</span>
                                                <span className="text-green-600 font-medium">
                                                    {selectedApi.recent_changes.added || 0}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Modified:</span>
                                                <span className="text-yellow-600 font-medium">
                                                    {selectedApi.recent_changes.modified || 0}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Removed:</span>
                                                <span className="text-red-600 font-medium">
                                                    {selectedApi.recent_changes.removed || 0}
                                                </span>
                                            </div>
                                        </div>
                                    ) : (
                                        <p className="text-gray-500">No recent changes</p>
                                    )}
                                </div>
                                
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-3">Scan Information</h3>
                                    <div className="space-y-2 text-sm">
                                        <div>
                                            <span className="text-gray-600">Last Scan:</span>
                                            <span className="ml-2">{formatTimestamp(selectedApi.last_scan_timestamp)}</span>
                                        </div>
                                        <div>
                                            <span className="text-gray-600">Status:</span>
                                            <span className="ml-2 capitalize">{selectedApi.last_scan_status}</span>
                                        </div>
                                        <div>
                                            <span className="text-gray-600">Total Endpoints:</span>
                                            <span className="ml-2">{selectedApi.total_endpoints}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            {selectedApi.changes && selectedApi.changes.scans && (
                                <div className="mt-6">
                                    <h3 className="font-medium text-gray-900 mb-3">Scan History</h3>
                                    <div className="space-y-2">
                                        {selectedApi.changes.scans.slice(0, 3).map((scan, index) => (
                                            <div key={index} className="border border-gray-200 rounded p-3">
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm font-medium">
                                                        {formatTimestamp(scan.timestamp)}
                                                    </span>
                                                    <span className="text-sm text-gray-500">
                                                        {scan.endpoints_count} endpoints
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard; 