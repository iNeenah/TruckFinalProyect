import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useTheme } from '../../contexts/ThemeContext';

interface LayoutProps {
  children?: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  const { actualTheme } = useTheme();

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${actualTheme === 'dark' ? 'dark' : ''}`}>
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar */}
        <Sidebar />
        
        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <Header />
          
          {/* Content */}
          <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
            <div className="container mx-auto px-6 py-8">
              {children || <Outlet />}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default Layout;