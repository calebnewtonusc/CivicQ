/**
 * Tests for Navbar component
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { axe, toHaveNoViolations } from 'jest-axe';
import Navbar from '../Navbar';

expect.extend(toHaveNoViolations);

// Mock AuthContext
const mockAuthContext = {
  user: null,
  login: jest.fn(),
  logout: jest.fn(),
  loading: false,
};

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext,
}));

const renderNavbar = (props = {}) => {
  return render(
    <BrowserRouter>
      <Navbar {...props} />
    </BrowserRouter>
  );
};

describe('Navbar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders navbar with logo', () => {
      renderNavbar();
      expect(screen.getByText(/CivicQ/i)).toBeInTheDocument();
    });

    it('shows login button when not authenticated', () => {
      renderNavbar();
      expect(screen.getByText(/log in/i)).toBeInTheDocument();
      expect(screen.getByText(/sign up/i)).toBeInTheDocument();
    });

    it('shows user menu when authenticated', () => {
      mockAuthContext.user = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'voter',
      };

      renderNavbar();
      expect(screen.getByText(/Test User/i)).toBeInTheDocument();
      expect(screen.queryByText(/log in/i)).not.toBeInTheDocument();
    });

    it('shows different options for candidate role', () => {
      mockAuthContext.user = {
        id: 2,
        email: 'candidate@example.com',
        full_name: 'Jane Candidate',
        role: 'candidate',
      };

      renderNavbar();
      expect(screen.getByText(/candidate portal/i)).toBeInTheDocument();
    });

    it('shows admin link for admin users', () => {
      mockAuthContext.user = {
        id: 3,
        email: 'admin@example.com',
        full_name: 'Admin User',
        role: 'admin',
      };

      renderNavbar();
      expect(screen.getByText(/admin/i)).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('opens mobile menu when hamburger is clicked', async () => {
      renderNavbar();

      // Find and click mobile menu button
      const menuButton = screen.getByLabelText(/open menu/i);
      fireEvent.click(menuButton);

      await waitFor(() => {
        expect(screen.getByRole('navigation')).toHaveClass('open');
      });
    });

    it('calls logout when logout is clicked', async () => {
      mockAuthContext.user = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'voter',
      };

      renderNavbar();

      const logoutButton = screen.getByText(/log out/i);
      fireEvent.click(logoutButton);

      await waitFor(() => {
        expect(mockAuthContext.logout).toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility', () => {
    it('has no accessibility violations', async () => {
      const { container } = renderNavbar();
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has proper ARIA labels', () => {
      renderNavbar();
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('is keyboard navigable', () => {
      renderNavbar();
      const links = screen.getAllByRole('link');

      links.forEach(link => {
        expect(link).toHaveAttribute('tabIndex', '0');
      });
    });
  });

  describe('Responsive Behavior', () => {
    it('shows mobile menu button on small screens', () => {
      // Mock window.innerWidth
      global.innerWidth = 500;
      renderNavbar();

      expect(screen.getByLabelText(/open menu/i)).toBeInTheDocument();
    });
  });
});
