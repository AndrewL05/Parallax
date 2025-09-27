import { useState, useCallback } from "react";
import { useAuth } from "@clerk/clerk-react";
import { simulationService } from "../services/simulationService";
import type { SimulationResult, UserContext } from "../types/api";
import type { SimulationFormData } from "../types/simulation";

export const useSimulation = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { getToken, isSignedIn } = useAuth();

  const createSimulation = useCallback(
    async (formData: SimulationFormData): Promise<SimulationResult> => {
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

        // Transform user context data to match backend expectations
        const transformedUserContext: Partial<UserContext> = {
          age: formData.user_context.age ? parseInt(formData.user_context.age, 10) : null,
          current_location: formData.user_context.current_location || undefined,
          current_salary: formData.user_context.current_salary ? parseInt(formData.user_context.current_salary, 10) : null,
          education_level: formData.user_context.education_level || undefined,
        };

        // Clean up empty values
        Object.keys(transformedUserContext).forEach((key) => {
          const value = transformedUserContext[key as keyof UserContext];
          if (value === null || value === "" || value === undefined) {
            delete transformedUserContext[key as keyof UserContext];
          }
        });

        // Re-enable authentication now that auth sync is fixed
        const token = isSignedIn ? await getToken() : null;
        const result = await simulationService.createSimulation(
          {
            choice_a: formData.choice_a,
            choice_b: formData.choice_b,
            user_context: Object.keys(transformedUserContext).length > 0 ? transformedUserContext : undefined
          },
          token || undefined
        );
        setSimulation(result);
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
        console.error("❌ Simulation error details:", err);
        setError(errorMessage);
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