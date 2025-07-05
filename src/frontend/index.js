/**
 * @file index.js
 * @brief Main entry point for the React application
 * @author Huy Le (huyisme-005)
 * @description 
 *     Entry point for the NL2Flow admin dashboard React application.
 *     Sets up the root component and renders the application to the DOM.
 * 
 *     Key Features:
 *     - React 18 createRoot API
 *     - Strict mode for development
 *     - Global CSS imports
 *     - Error boundary setup
 * 
 *     Potential Issues:
 *     - Missing root element
 *     - CSS import failures
 *     - React version compatibility
 * 
 *     Debugging Tips:
 *     - Check for root element in public/index.html
 *     - Verify React version compatibility
 *     - Monitor console for import errors
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

// Get the root element
const container = document.getElementById('root');

// Check if root element exists
if (!container) {
    throw new Error('Root element not found. Make sure there is a <div id="root"></div> in your HTML.');
}

// Create root and render app
const root = createRoot(container);

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
); 