import React, { useEffect, useRef, useReducer } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import DemoModeBanner from './DemoModeBanner';
import SkipLinks from './SkipLinks';

interface LayoutProps {
  children: React.ReactNode;
}

type VisibilityAction = { type: 'HIDE' } | { type: 'SHOW' };

function visibilityReducer(_state: boolean, action: VisibilityAction): boolean {
  switch (action.type) {
    case 'HIDE': return false;
    case 'SHOW': return true;
    default: return _state;
  }
}

const PageTransition: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const [isVisible, dispatch] = useReducer(visibilityReducer, false);
  const prevPath = useRef<string | null>(null);

  useEffect(() => {
    if (prevPath.current !== location.pathname) {
      dispatch({ type: 'HIDE' });
      const id = requestAnimationFrame(() => {
        requestAnimationFrame(() => dispatch({ type: 'SHOW' }));
      });
      prevPath.current = location.pathname;
      return () => cancelAnimationFrame(id);
    } else {
      dispatch({ type: 'SHOW' });
    }
  }, [location.pathname]);

  return (
    <div
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(6px)',
        transition: 'opacity 260ms ease-out, transform 260ms ease-out',
      }}
    >
      {children}
    </div>
  );
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-surface-subtle flex flex-col">
      <SkipLinks />
      <DemoModeBanner />
      <Navbar />
      <main
        id="main-content"
        className="flex-grow"
        role="main"
        aria-label="Main content"
      >
        <PageTransition>{children}</PageTransition>
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
