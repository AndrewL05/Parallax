import { useEffect } from "react";
import { useAuth as useClerkAuth, useUser } from "@clerk/clerk-react";
import { simulationService } from "../services/simulationService";

export const useAuth = () => {
  const { getToken, isSignedIn, isLoaded } = useClerkAuth();
  const { user } = useUser();

  useEffect(() => {
    const syncProfile = async () => {
      if (isSignedIn && user && isLoaded) {
        try {
          const token = await getToken();
          await simulationService.syncUserProfile(
            {
              id: user.id,
              email: user.primaryEmailAddress?.emailAddress,
              firstName: user.firstName || undefined,
              lastName: user.lastName || undefined,
            },
            token || undefined
          );
        } catch (error) {
          console.error("Profile sync failed:", error);
        }
      }
    };

    syncProfile();
  }, [isSignedIn, user, getToken, isLoaded]);

  return {
    isSignedIn,
    isLoaded,
    user,
    getToken,
  };
};
