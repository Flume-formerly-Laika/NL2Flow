/**
 * @file ScanHistory.js
 * @brief Scan history component for displaying scan execution history
 * @author Huy Le (huyisme-005)
 * @description 
 *     Displays detailed history of API scan executions including
 *     timestamps, results, and performance metrics. Provides insights
 *     into scan patterns and system health.
 * 
 *     Key Features:
 *     - Chronological scan history
 *     - Success/failure rates
 *     - Performance metrics
 *     - Detailed result breakdown
 * 
 *     Potential Issues:
 *     - Large history datasets
 *     - Real-time updates
 *     - Data pagination
 * 
 *     Debugging Tips:
 *     - Monitor data loading performance
 *     - Check for memory leaks with large datasets
 *     - Verify timestamp formatting
 */

import React, { useState } from 'react';
import { Calendar, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const ScanHistory = ({ data, loading, error }) => {
    const [selectedScan, setSelectedScan] = useState(null);
    const [showDetails, setShowDetails] = useState(false);

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
                    <div className="space-y-3">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-16 bg-gray-200 rounded"></div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center text-red-600">
                    <XCircle className="w-8 h-8 mx-auto mb-2" />
                    <p>Error loading scan history: {error}</p>
                </div>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center text-gray-500">
                    <Calendar className="w-8 h-8 mx-auto mb-2" />
                    <p>No scan history available</p>
                </div>
            </div>
        );
    }

    const formatTimestamp = (timestamp) => {
        return new Date(timestamp * 1000).toLocaleString();
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'success':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case 'error':
                return <XCircle className="w-4 h-4 text-red-500" />;
            default:
                return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
        }
    };

    const handleScanClick = (scan) => {
        setSelectedScan(scan);
        setShowDetails(true);
    };

    return (
        <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Scan History</h2>
                <p className="text-sm text-gray-600">Recent API scan executions</p>
            </div>
            
            <div className="p-6">
                <div className="space-y-4">
                    {data.map((scan) => (
                        <div 
                            key={scan.scan_id} 
                            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                            onClick={() => handleScanClick(scan)}
                        >
                            <div className="flex justify-between items-start mb-3">
                                <div>
                                    <h3 className="font-medium text-gray-900">
                                        Scan {scan.scan_id}
                                    </h3>
                                    <div className="flex items-center text-sm text-gray-500 mt-1">
                                        <Clock className="w-4 h-4 mr-1" />
                                        {formatTimestamp(scan.timestamp)}
                                    </div>
                                </div>
                                
                                <div className="text-right">
                                    <div className="flex items-center justify-end mb-1">
                                        {getStatusIcon(scan.successful_scans === scan.total_apis_scanned ? 'success' : 'error')}
                                        <span className="ml-1 text-sm font-medium">
                                            {scan.successful_scans}/{scan.total_apis_scanned} successful
                                        </span>
                                    </div>
                                    <div className="text-xs text-gray-500">
                                        {scan.results?.length || 0} APIs scanned
                                    </div>
                                </div>
                            </div>
                            
                            {scan.results && scan.results.length > 0 && (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                                    {scan.results.slice(0, 6).map((result) => (
                                        <div key={result.api_name} className="flex items-center text-xs">
                                            {getStatusIcon(result.status)}
                                            <span className="ml-1 font-medium">{result.api_name}</span>
                                            {result.endpoints_count > 0 && (
                                                <span className="text-gray-500 ml-1">
                                                    ({result.endpoints_count})
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                    {scan.results.length > 6 && (
                                        <div className="text-xs text-gray-500">
                                            +{scan.results.length - 6} more...
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Scan Details Modal */}
            {showDetails && selectedScan && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <div className="flex justify-between items-center">
                                <h2 className="text-xl font-semibold text-gray-900">
                                    Scan Details: {selectedScan.scan_id}
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
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-3">Scan Information</h3>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Scan ID:</span>
                                            <span className="font-medium">{selectedScan.scan_id}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Timestamp:</span>
                                            <span className="font-medium">{formatTimestamp(selectedScan.timestamp)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Total APIs:</span>
                                            <span className="font-medium">{selectedScan.total_apis_scanned}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Successful:</span>
                                            <span className="font-medium text-green-600">{selectedScan.successful_scans}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Failed:</span>
                                            <span className="font-medium text-red-600">
                                                {selectedScan.total_apis_scanned - selectedScan.successful_scans}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-3">Performance</h3>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Success Rate:</span>
                                            <span className="font-medium">
                                                {selectedScan.total_apis_scanned > 0 
                                                    ? Math.round((selectedScan.successful_scans / selectedScan.total_apis_scanned) * 100)
                                                    : 0}%
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Total Endpoints:</span>
                                            <span className="font-medium">
                                                {selectedScan.results?.reduce((sum, result) => sum + (result.endpoints_count || 0), 0) || 0}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            {selectedScan.results && selectedScan.results.length > 0 && (
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-3">API Results</h3>
                                    <div className="space-y-2">
                                        {selectedScan.results.map((result) => (
                                            <div key={result.api_name} className="border border-gray-200 rounded p-3">
                                                <div className="flex justify-between items-center">
                                                    <div className="flex items-center">
                                                        {getStatusIcon(result.status)}
                                                        <span className="ml-2 font-medium">{result.api_name}</span>
                                                    </div>
                                                    <div className="text-sm text-gray-600">
                                                        {result.endpoints_count} endpoints
                                                    </div>
                                                </div>
                                                {result.error && (
                                                    <div className="mt-2 text-sm text-red-600">
                                                        Error: {result.error}
                                                    </div>
                                                )}
                                                {result.changes_detected && result.changes_summary && (
                                                    <div className="mt-2 text-sm text-yellow-600">
                                                        Changes detected: {result.changes_summary.total_changes || 0} changes
                                                    </div>
                                                )}
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

export default ScanHistory; 