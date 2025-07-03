import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from '../components/Dashboard';
import ApiSummary from '../components/ApiSummary';
import ScanHistory from '../components/ScanHistory';
import ApiChanges from '../components/ApiChanges';
import Navbar from '../components/Navbar';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <div className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/api-summary" element={<ApiSummary />} />
              <Route path="/scan-history" element={<ScanHistory />} />
              <Route path="/api-changes/:apiName" element={<ApiChanges />} />
            </Routes>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 