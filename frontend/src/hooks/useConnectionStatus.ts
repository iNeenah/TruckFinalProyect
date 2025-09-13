import { useState, useEffect } from 'react';
import { checkConnection } from '../services/apiClient';
import { toast } from 'react-hot-toast';

export const useConnectionStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isApiConnected, setIsApiConnected] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  // Check network status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success('Conexión restaurada');
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      toast.error('Sin conexión a internet');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Check API connection
  useEffect(() => {
    const checkApiConnection = async () => {
      if (!isOnline) {
        setIsApiConnected(false);
        return;
      }

      try {
        const connected = await checkConnection();
        setIsApiConnected(connected);
        setLastChecked(new Date());
        
        if (!connected && isOnline) {
          toast.error('No se puede conectar al servidor');
        }
      } catch (error) {
        setIsApiConnected(false);
        setLastChecked(new Date());
      }
    };

    // Initial check
    checkApiConnection();

    // Check every 30 seconds
    const interval = setInterval(checkApiConnection, 30000);

    return () => clearInterval(interval);
  }, [isOnline]);

  const forceCheck = async () => {
    try {
      const connected = await checkConnection();
      setIsApiConnected(connected);
      setLastChecked(new Date());
      return connected;
    } catch (error) {
      setIsApiConnected(false);
      setLastChecked(new Date());
      return false;
    }
  };

  return {
    isOnline,
    isApiConnected,
    isConnected: isOnline && isApiConnected,
    lastChecked,
    forceCheck,
  };
};

export default useConnectionStatus;