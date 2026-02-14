import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import DemoModeBanner from './DemoModeBanner';
import SkipLinks from './SkipLinks';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <SkipLinks />
      <DemoModeBanner />
      <Navbar />
      <main id="main-content" className="flex-grow" role="main" aria-label="Main content">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
