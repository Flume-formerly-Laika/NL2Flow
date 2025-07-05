/**
 * @file ApiChanges.js
 * @brief API changes component for displaying schema change details
 * @author Huy Le (huyisme-005)
 * @description 
 *     Displays detailed information about API schema changes including
 *     diff reports, field-level changes, and change history. Provides
 *     comprehensive view of what changed between API versions.
 * 
 *     Key Features:
 *     - Detailed diff visualization
 *     - Field-level change tracking
 *     - Change history timeline
 *     - Change impact assessment
 * 
 *     Potential Issues:
 *     - Complex diff rendering
 *     - Large change datasets
 *     - Real-time diff updates
 * 
 *     Debugging Tips:
 *     - Test with various diff scenarios
 *     - Monitor rendering performance
 *     - Verify diff data structure
 */

import React, { useState, useEffect } from 'react';
import { Plus, Minus, Edit, AlertTriangle, Info } from 'lucide-react';

const ApiChanges = ({ apiName, changes, loading, error }) => {
    const [selectedChangeType, setSelectedChangeType] = useState('all');
    const [expandedChanges, setExpandedChanges] = useState(new Set());

    useEffect(() => {
        if (changes) {
            // Auto-expand changes if there are few items
            const totalChanges = (changes.added_endpoints?.length || 0) + 
                               (changes.removed_endpoints?.length || 0) + 
                               (changes.modified_endpoints?.length || 0);
            if (totalChanges <= 5) {
                setExpandedChanges(new Set(['added', 'removed', 'modified']));
            }
        }
    }, [changes]);

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
                    <div className="space-y-3">
                        <div className="h-8 bg-gray-200 rounded"></div>
                        <div className="h-8 bg-gray-200 rounded"></div>
                        <div className="h-8 bg-gray-200 rounded"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center text-red-600">
                    <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                    <p>Error loading changes: {error}</p>
                </div>
            </div>
        );
    }

    if (!changes) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center text-gray-500">
                    <Info className="w-8 h-8 mx-auto mb-2" />
                    <p>No changes data available for {apiName}</p>
                </div>
            </div>
        );
    }

    const toggleExpanded = (changeType) => {
        const newExpanded = new Set(expandedChanges);
        if (newExpanded.has(changeType)) {
            newExpanded.delete(changeType);
        } else {
            newExpanded.add(changeType);
        }
        setExpandedChanges(newExpanded);
    };

    const getChangeCount = (changeType) => {
        switch (changeType) {
            case 'added':
                return changes.added_endpoints?.length || 0;
            case 'removed':
                return changes.removed_endpoints?.length || 0;
            case 'modified':
                return changes.modified_endpoints?.length || 0;
            default:
                return (changes.added_endpoints?.length || 0) + 
                       (changes.removed_endpoints?.length || 0) + 
                       (changes.modified_endpoints?.length || 0);
        }
    };

    const renderEndpointChange = (endpoint, type) => {
        const isExpanded = expandedChanges.has(type);
        
        return (
            <div key={`${endpoint.method}-${endpoint.path}`} className="border border-gray-200 rounded p-3 mb-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center">
                        {type === 'added' && <Plus className="w-4 h-4 text-green-500 mr-2" />}
                        {type === 'removed' && <Minus className="w-4 h-4 text-red-500 mr-2" />}
                        {type === 'modified' && <Edit className="w-4 h-4 text-yellow-500 mr-2" />}
                        
                        <div>
                            <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded mr-2">
                                {endpoint.method}
                            </span>
                            <span className="font-medium">{endpoint.path}</span>
                        </div>
                    </div>
                    
                    <button
                        onClick={() => toggleExpanded(type)}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        {isExpanded ? '▼' : '▶'}
                    </button>
                </div>
                
                {isExpanded && endpoint.schema && (
                    <div className="mt-3 pl-6 border-l-2 border-gray-200">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <h4 className="font-medium text-sm text-gray-700 mb-2">Input Schema</h4>
                                <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                                    {JSON.stringify(endpoint.schema.input, null, 2)}
                                </pre>
                            </div>
                            <div>
                                <h4 className="font-medium text-sm text-gray-700 mb-2">Output Schema</h4>
                                <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                                    {JSON.stringify(endpoint.schema.output, null, 2)}
                                </pre>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };

    const renderFieldChanges = () => {
        if (!changes.field_changes) return null;

        const { added, removed, changed } = changes.field_changes;
        
        return (
            <div className="mt-6">
                <h3 className="font-medium text-gray-900 mb-3">Field-Level Changes</h3>
                
                {Object.keys(added).length > 0 && (
                    <div className="mb-4">
                        <h4 className="text-sm font-medium text-green-700 mb-2 flex items-center">
                            <Plus className="w-4 h-4 mr-1" />
                            Added Fields ({Object.keys(added).length})
                        </h4>
                        <div className="space-y-1">
                            {Object.entries(added).map(([field, type]) => (
                                <div key={field} className="text-sm bg-green-50 p-2 rounded">
                                    <span className="font-mono">{field}</span>
                                    <span className="text-green-600 ml-2">→ {type}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                
                {Object.keys(removed).length > 0 && (
                    <div className="mb-4">
                        <h4 className="text-sm font-medium text-red-700 mb-2 flex items-center">
                            <Minus className="w-4 h-4 mr-1" />
                            Removed Fields ({Object.keys(removed).length})
                        </h4>
                        <div className="space-y-1">
                            {Object.entries(removed).map(([field, type]) => (
                                <div key={field} className="text-sm bg-red-50 p-2 rounded">
                                    <span className="font-mono">{field}</span>
                                    <span className="text-red-600 ml-2">→ {type}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                
                {Object.keys(changed).length > 0 && (
                    <div className="mb-4">
                        <h4 className="text-sm font-medium text-yellow-700 mb-2 flex items-center">
                            <Edit className="w-4 h-4 mr-1" />
                            Modified Fields ({Object.keys(changed).length})
                        </h4>
                        <div className="space-y-1">
                            {Object.entries(changed).map(([field, change]) => (
                                <div key={field} className="text-sm bg-yellow-50 p-2 rounded">
                                    <span className="font-mono">{field}</span>
                                    <span className="text-yellow-600 ml-2">
                                        {change.old_type} → {change.new_type}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">API Changes: {apiName}</h2>
                <p className="text-sm text-gray-600">Detailed schema change information</p>
            </div>
            
            <div className="p-6">
                {/* Change Summary */}
                {changes.diff_summary && (
                    <div className="mb-6">
                        <h3 className="font-medium text-gray-900 mb-3">Change Summary</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-green-50 p-3 rounded">
                                <div className="flex items-center">
                                    <Plus className="w-5 h-5 text-green-600 mr-2" />
                                    <div>
                                        <div className="text-lg font-semibold text-green-600">
                                            {changes.diff_summary.endpoint_changes?.added || 0}
                                        </div>
                                        <div className="text-sm text-green-700">Added Endpoints</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-red-50 p-3 rounded">
                                <div className="flex items-center">
                                    <Minus className="w-5 h-5 text-red-600 mr-2" />
                                    <div>
                                        <div className="text-lg font-semibold text-red-600">
                                            {changes.diff_summary.endpoint_changes?.removed || 0}
                                        </div>
                                        <div className="text-sm text-red-700">Removed Endpoints</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-yellow-50 p-3 rounded">
                                <div className="flex items-center">
                                    <Edit className="w-5 h-5 text-yellow-600 mr-2" />
                                    <div>
                                        <div className="text-lg font-semibold text-yellow-600">
                                            {changes.diff_summary.endpoint_changes?.modified || 0}
                                        </div>
                                        <div className="text-sm text-yellow-700">Modified Endpoints</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Change Type Filter */}
                <div className="mb-6">
                    <div className="flex space-x-2">
                        {['all', 'added', 'removed', 'modified'].map(type => (
                            <button
                                key={type}
                                onClick={() => setSelectedChangeType(type)}
                                className={`px-3 py-1 rounded text-sm font-medium ${
                                    selectedChangeType === type
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                            >
                                {type.charAt(0).toUpperCase() + type.slice(1)} ({getChangeCount(type)})
                            </button>
                        ))}
                    </div>
                </div>

                {/* Added Endpoints */}
                {selectedChangeType === 'all' || selectedChangeType === 'added' ? (
                    changes.added_endpoints && changes.added_endpoints.length > 0 && (
                        <div className="mb-6">
                            <h3 className="font-medium text-green-700 mb-3 flex items-center">
                                <Plus className="w-5 h-5 mr-2" />
                                Added Endpoints ({changes.added_endpoints.length})
                            </h3>
                            <div className="space-y-2">
                                {changes.added_endpoints.map(endpoint => 
                                    renderEndpointChange(endpoint, 'added')
                                )}
                            </div>
                        </div>
                    )
                ) : null}

                {/* Removed Endpoints */}
                {selectedChangeType === 'all' || selectedChangeType === 'removed' ? (
                    changes.removed_endpoints && changes.removed_endpoints.length > 0 && (
                        <div className="mb-6">
                            <h3 className="font-medium text-red-700 mb-3 flex items-center">
                                <Minus className="w-5 h-5 mr-2" />
                                Removed Endpoints ({changes.removed_endpoints.length})
                            </h3>
                            <div className="space-y-2">
                                {changes.removed_endpoints.map(endpoint => 
                                    renderEndpointChange(endpoint, 'removed')
                                )}
                            </div>
                        </div>
                    )
                ) : null}

                {/* Modified Endpoints */}
                {selectedChangeType === 'all' || selectedChangeType === 'modified' ? (
                    changes.modified_endpoints && changes.modified_endpoints.length > 0 && (
                        <div className="mb-6">
                            <h3 className="font-medium text-yellow-700 mb-3 flex items-center">
                                <Edit className="w-5 h-5 mr-2" />
                                Modified Endpoints ({changes.modified_endpoints.length})
                            </h3>
                            <div className="space-y-2">
                                {changes.modified_endpoints.map(endpoint => 
                                    renderEndpointChange(endpoint, 'modified')
                                )}
                            </div>
                        </div>
                    )
                ) : null}

                {/* Field-Level Changes */}
                {renderFieldChanges()}

                {/* No Changes Message */}
                {getChangeCount(selectedChangeType) === 0 && (
                    <div className="text-center text-gray-500 py-8">
                        <Info className="w-8 h-8 mx-auto mb-2" />
                        <p>No {selectedChangeType} changes found</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ApiChanges; 