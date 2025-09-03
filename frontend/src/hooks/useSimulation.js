import { useState, useCallback } from "react";
import { useAuth } from "@clerk/clerk-react";
import { simulationService } from "../services/simulationService";

export const useSimulation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [simulation, setSimulation] = useState(null);
  const [error, setError] = useState(null);
  const { getToken, isSignedIn } = useAuth();

  const createSimulation = useCallback(
    async (formData) => {
      setIsLoading(true);
      setError(null);

      try {
        console.log("📤 Raw form data received:", formData);
        console.log(
          "📤 Sending simulation data:",
          JSON.stringify(formData, null, 2)
        );

        // Validate data structure before sending
        if (!formData.choice_a || !formData.choice_b) {
          throw new Error("Missing choice_a or choice_b");
        }
        if (!formData.choice_a.title || !formData.choice_b.title) {
          throw new Error("Missing titles for choices");
        }

        // Re-enable authentication now that auth sync is fixed
        const token = isSignedIn ? await getToken() : null;
        const result = await simulationService.createSimulation(
          formData,
          token
        );
        setSimulation(result);
        return result;
      } catch (err) {
        console.error("❌ Simulation error details:", err);
        setError(err.message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [getToken, isSignedIn]
  );

  const resetSimulation = useCallback(() => {
    setSimulation(null);
    setError(null);
  }, []);

  return {
    simulation,
    isLoading,
    error,
    createSimulation,
    resetSimulation,
  };
};
