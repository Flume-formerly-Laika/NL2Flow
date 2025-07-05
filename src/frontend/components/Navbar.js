/**
 * @file Navbar.js
 * @brief Navigation bar component for the admin dashboard
 * @author Huy Le (huyisme-005)
 * @description 
 *     Provides navigation between different sections of the admin dashboard
 *     including dashboard overview, scan history, and settings. Includes
 *     branding and user interface elements.
 * 
 *     Key Features:
 *     - Responsive navigation menu
 *     - Active page highlighting
 *     - Branding and logo
 *     - User status indicators
 * 
 *     Potential Issues:
 *     - Mobile responsiveness
 *     - Active state management
 *     - Navigation state persistence
 * 
 *     Debugging Tips:
 *     - Test on different screen sizes
 *     - Verify active state logic
 *     - Check navigation event handling
 */

import React, { useState } from 'react';
import { Menu, X, Activity, History, Settings, Home } from 'lucide-react';

const Navbar = ({ activePage, onPageChange }) => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const navigationItems = [
        { id: 'dashboard', label: 'Dashboard', icon: Home },
        { id: 'history', label: 'Scan History', icon: History },
        { id: 'changes', label: 'API Changes', icon: Activity },
        { id: 'settings', label: 'Settings', icon: Settings },
    ];

    const handleNavClick = (pageId) => {
        onPageChange(pageId);
        setIsMobileMenuOpen(false);
    };

    return (
        <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    {/* Logo and Brand */}
                    <div className="flex items-center">
                        <div className="flex-shrink-0 flex items-center">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                <Activity className="w-5 h-5 text-white" />
                            </div>
                            <div className="ml-3">
                                <h1 className="text-xl font-bold text-gray-900">NL2Flow</h1>
                                <p className="text-xs text-gray-500">API Watchdog</p>
                            </div>
                        </div>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {navigationItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <button
                                    key={item.id}
                                    onClick={() => handleNavClick(item.id)}
                                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                        activePage === item.id
                                            ? 'bg-blue-100 text-blue-700'
                                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                                    }`}
                                >
                                    <Icon className="w-4 h-4 mr-2" />
                                    {item.label}
                                </button>
                            );
                        })}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                        >
                            {isMobileMenuOpen ? (
                                <X className="w-6 h-6" />
                            ) : (
                                <Menu className="w-6 h-6" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation Menu */}
            {isMobileMenuOpen && (
                <div className="md:hidden">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
                        {navigationItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <button
                                    key={item.id}
                                    onClick={() => handleNavClick(item.id)}
                                    className={`flex items-center w-full px-3 py-2 rounded-md text-base font-medium transition-colors ${
                                        activePage === item.id
                                            ? 'bg-blue-100 text-blue-700'
                                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                                    }`}
                                >
                                    <Icon className="w-5 h-5 mr-3" />
                                    {item.label}
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar; 