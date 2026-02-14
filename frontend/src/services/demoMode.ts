// Demo Mode Service
// Provides a flag to track when we're in demo mode (backend unavailable)

let isDemoMode = false;

export const setDemoMode = (enabled: boolean) => {
  isDemoMode = enabled;
  if (enabled) {
    console.log('CivicQ is running in DEMO MODE - using mock data');
  }
};

export const getDemoMode = (): boolean => {
  return isDemoMode;
};

// Check if we should use demo mode based on API availability
export const checkBackendAvailability = async (
  apiClient: any
): Promise<boolean> => {
  try {
    // Try to ping the backend health endpoint
    await apiClient.get('/health', { timeout: 3000 });
    setDemoMode(false);
    return true;
  } catch (error) {
    // Backend is unavailable, enable demo mode
    setDemoMode(true);
    return false;
  }
};
