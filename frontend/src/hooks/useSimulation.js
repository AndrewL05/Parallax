import { useState, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { simulationService } from '../services/simulationService';

export const useSimulation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [simulation, setSimulation] = useState(null);
  const [error, setError] = useState(null);
  const { getToken, isSignedIn } = useAuth();

  const createSimulation = useCallback(async (formData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = isSignedIn ? await getToken() : null;
      const result = await simulationService.createSimulation(formData, token);
      setSimulation(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn]);

  const resetSimulation = useCallback(() => {
    setSimulation(null);
    setError(null);
  }, []);

  return {
    simulation,
    isLoading,
    error,
    createSimulation,
    resetSimulation
  };
};