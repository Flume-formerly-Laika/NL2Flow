/**
 * @file ApiSummary.js
 * @brief API summary component for displaying scan results and statistics
 * @author Huy Le (huyisme-005)
 * @description 
 *     Displays detailed summary information about API scans including
 *     statistics, recent changes, and performance metrics. Used as a
 *     standalone component or within the main dashboard.
 * 
 *     Key Features:
 *     - Scan statistics and metrics
 *     - Change detection summary
 *     - Performance indicators
 *     - Historical trend data
 * 
 *     Potential Issues:
 *     - Data loading delays
 *     - Large datasets causing performance issues
 *     - Missing data handling
 * 
 *     Debugging Tips:
 *     - Check data format from API
 *     - Monitor component re-renders
 *     - Verify prop types and data structure
 */

import React from 'react';
import { TrendingUp, TrendingDown, Activity, Clock } from 'lucide-react';

const ApiSummary = ({ data, loading, error }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                    <div className="space-y-3">
                        <div className="h-3 bg-gray-200 rounded"></div>
                        <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                        <div className="h-3 bg-gray-200 rounded w-4/6"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center text-red-600">
                    <p>Error loading API summary: {error}</p>
                </div>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center text-gray-500">
                    <p>No API data available</p>
                </div>
            </div>
        );
    }

    // Calculate summary statistics
    const totalApis = data.length;
    const successfulScans = data.filter(api => api.last_scan_status === 'success').length;
    const failedScans = totalApis - successfulScans;
    const apisWithChanges = data.filter(api => 
        api.recent_changes && 
        Object.values(api.recent_changes).some(count => count > 0)
    ).length;

    const totalEndpoints = data.reduce((sum, api) => sum + (api.total_endpoints || 0), 0);
    const averageEndpoints = totalApis > 0 ? Math.round(totalEndpoints / totalApis) : 0;

    return (
        <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">API Summary</h2>
                <p className="text-sm text-gray-600">Overview of all monitored APIs</p>
            </div>
            
            <div className="p-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{totalApis}</div>
                        <div className="text-sm text-gray-600">Total APIs</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{successfulScans}</div>
                        <div className="text-sm text-gray-600">Successful</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{failedScans}</div>
                        <div className="text-sm text-gray-600">Failed</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600">{apisWithChanges}</div>
                        <div className="text-sm text-gray-600">With Changes</div>
                    </div>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center mb-2">
                            <Activity className="w-5 h-5 text-blue-500 mr-2" />
                            <h3 className="font-medium text-gray-900">Endpoint Statistics</h3>
                        </div>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span>Total Endpoints:</span>
                                <span className="font-medium">{totalEndpoints}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Average per API:</span>
                                <span className="font-medium">{averageEndpoints}</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center mb-2">
                            <Clock className="w-5 h-5 text-green-500 mr-2" />
                            <h3 className="font-medium text-gray-900">Recent Activity</h3>
                        </div>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span>Last 24h scans:</span>
                                <span className="font-medium">
                                    {data.filter(api => {
                                        const lastScan = new Date(api.last_scan_timestamp * 1000);
                                        const now = new Date();
                                        return (now - lastScan) < 24 * 60 * 60 * 1000;
                                    }).length}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span>Last 7 days:</span>
                                <span className="font-medium">
                                    {data.filter(api => {
                                        const lastScan = new Date(api.last_scan_timestamp * 1000);
                                        const now = new Date();
                                        return (now - lastScan) < 7 * 24 * 60 * 60 * 1000;
                                    }).length}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* API Status Breakdown */}
                <div>
                    <h3 className="font-medium text-gray-900 mb-3">API Status Breakdown</h3>
                    <div className="space-y-2">
                        {data.map(api => (
                            <div key={api.api_name} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                                <div className="flex items-center">
                                    <div className={`w-3 h-3 rounded-full mr-3 ${
                                        api.last_scan_status === 'success' ? 'bg-green-500' : 'bg-red-500'
                                    }`}></div>
                                    <span className="font-medium text-gray-900">{api.api_name}</span>
                                </div>
                                <div className="text-sm text-gray-600">
                                    {api.total_endpoints} endpoints
                                    {api.recent_changes && Object.values(api.recent_changes).some(count => count > 0) && (
                                        <span className="ml-2 text-yellow-600">
                                            • Changes detected
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ApiSummary; 