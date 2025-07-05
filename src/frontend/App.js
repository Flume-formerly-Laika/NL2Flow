/**
 * @file App.js
 * @brief Main application component for NL2Flow admin dashboard
 * @author Huy Le (huyisme-005)
 * @description 
 *     Main application component that orchestrates the admin dashboard,
 *     manages navigation between different views, and handles data fetching
 *     for all components. Integrates with the FastAPI backend for data
 *     and provides a unified user interface.
 * 
 *     Key Features:
 *     - Multi-page navigation
 *     - Data management and state
 *     - Error handling and loading states
 *     - Responsive design
 *     - Real-time data updates
 * 
 *     Component Structure:
 *     - Navbar: Navigation between views
 *     - Dashboard: Main overview page
 *     - ScanHistory: Detailed scan history
 *     - ApiChanges: Schema change details
 *     - Settings: Configuration options
 * 
 *     Potential Issues:
 *     - API connection failures
 *     - State management complexity
 *     - Performance with large datasets
 *     - CORS and authentication issues
 * 
 *     Debugging Tips:
 *     - Check browser console for errors
 *     - Monitor network requests
 *     - Verify API endpoints
 *     - Test responsive design
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import ScanHistory from './components/ScanHistory';
import ApiChanges from './components/ApiChanges';
import ApiSummary from './components/ApiSummary';

const App = () => {
    const [activePage, setActivePage] = useState('dashboard');
    const [apiData, setApiData] = useState([]);
    const [scanHistory, setScanHistory] = useState([]);
    const [selectedApi, setSelectedApi] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // API base URL - should be configured via environment variables
    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

    /**
     * @function fetchData
     * @brief Fetch all necessary data from the backend
     * @description Loads API summary and scan history data for the dashboard
     */
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        
        try {
            const [apiResponse, historyResponse] = await Promise.all([
                axios.get(`${API_BASE_URL}/dashboard/api-summary`),
                axios.get(`${API_BASE_URL}/dashboard/scan-history?limit=10`)
            ]);
            
            setApiData(apiResponse.data);
            setScanHistory(historyResponse.data);
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to load dashboard data. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    };

    /**
     * @function handlePageChange
     * @brief Handle navigation between different pages
     * @param pageId ID of the page to navigate to
     * @description Updates the active page and manages component state
     */
    const handlePageChange = (pageId) => {
        setActivePage(pageId);
        
        // Clear selected API when navigating away from changes view
        if (pageId !== 'changes') {
            setSelectedApi(null);
        }
    };

    /**
     * @function handleApiSelect
     * @brief Handle API selection for detailed view
     * @param api API data object
     * @description Sets the selected API and navigates to changes view
     */
    const handleApiSelect = async (api) => {
        setSelectedApi(api);
        setActivePage('changes');
        
        // Fetch detailed changes for the selected API
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/api-changes/${api.api_name}?limit=5`);
            setSelectedApi(prev => ({ ...prev, changes: response.data }));
        } catch (err) {
            console.error('Error fetching API changes:', err);
            setError('Failed to load API changes');
        }
    };

    /**
     * @function handleRefresh
     * @brief Refresh all data from the backend
     * @description Reloads all dashboard data and clears any errors
     */
    const handleRefresh = () => {
        fetchData();
    };

    // Load data on component mount
    useEffect(() => {
        fetchData();

        // Set up auto-refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    // Render loading state
    if (loading && activePage === 'dashboard') {
        return (
            <div className="min-h-screen bg-gray-50">
                <Navbar activePage={activePage} onPageChange={handlePageChange} />
                <div className="flex items-center justify-center min-h-screen">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                        <p className="text-lg text-gray-600">Loading dashboard...</p>
                    </div>
                </div>
            </div>
        );
    }

    // Render error state
    if (error && activePage === 'dashboard') {
        return (
            <div className="min-h-screen bg-gray-50">
                <Navbar activePage={activePage} onPageChange={handlePageChange} />
                <div className="flex items-center justify-center min-h-screen">
                    <div className="text-center max-w-md mx-auto p-6">
                        <div className="text-red-500 text-6xl mb-4">⚠️</div>
                        <h2 className="text-xl font-semibold text-gray-800 mb-2">Connection Error</h2>
                        <p className="text-gray-600 mb-4">{error}</p>
                        <div className="space-x-4">
                            <button
                                onClick={handleRefresh}
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                                Retry
                            </button>
                            <button
                                onClick={() => window.location.reload()}
                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                            >
                                Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Render main application
    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar activePage={activePage} onPageChange={handlePageChange} />
            
            <main className="p-6">
                {activePage === 'dashboard' && (
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
                            <button
                                onClick={handleRefresh}
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center"
                            >
                                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                Refresh
                            </button>
                        </div>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <div className="lg:col-span-2">
                                <Dashboard 
                                    data={apiData}
                                    loading={loading}
                                    error={error}
                                    onApiSelect={handleApiSelect}
                                />
                            </div>
                            <div>
                                <ApiSummary 
                                    data={apiData}
                                    loading={loading}
                                    error={error}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activePage === 'history' && (
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-6">Scan History</h1>
                        <ScanHistory 
                            data={scanHistory}
                            loading={loading}
                            error={error}
                        />
                    </div>
                )}

                {activePage === 'changes' && (
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-6">
                            API Changes
                            {selectedApi && ` - ${selectedApi.api_name}`}
                        </h1>
                        
                        {selectedApi ? (
                            <ApiChanges 
                                apiName={selectedApi.api_name}
                                changes={selectedApi.changes}
                                loading={loading}
                                error={error}
                            />
                        ) : (
                            <div className="bg-white rounded-lg shadow p-6 text-center">
                                <p className="text-gray-500">
                                    Select an API from the dashboard to view its changes
                                </p>
                                <button
                                    onClick={() => setActivePage('dashboard')}
                                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                >
                                    Go to Dashboard
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {activePage === 'settings' && (
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration</h2>
                            
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        API Base URL
                                    </label>
                                    <input
                                        type="text"
                                        value={API_BASE_URL}
                                        readOnly
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                                    />
                                    <p className="text-sm text-gray-500 mt-1">
                                        Configure via REACT_APP_API_BASE_URL environment variable
                                    </p>
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Auto-refresh Interval
                                    </label>
                                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                                        <option value="30">30 seconds</option>
                                        <option value="60">1 minute</option>
                                        <option value="300">5 minutes</option>
                                        <option value="0">Disabled</option>
                                    </select>
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Scan History Limit
                                    </label>
                                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                                        <option value="10">10 entries</option>
                                        <option value="25">25 entries</option>
                                        <option value="50">50 entries</option>
                                        <option value="100">100 entries</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div className="mt-6 pt-6 border-t border-gray-200">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="text-gray-600">Version:</span>
                                        <span className="ml-2 font-medium">1.0.0</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">Environment:</span>
                                        <span className="ml-2 font-medium">
                                            {process.env.NODE_ENV || 'development'}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">Last Updated:</span>
                                        <span className="ml-2 font-medium">
                                            {new Date().toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">Status:</span>
                                        <span className="ml-2 font-medium text-green-600">Connected</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default App; 