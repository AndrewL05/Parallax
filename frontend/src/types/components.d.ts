// Type declarations for JSX components that haven't been migrated to TypeScript yet

declare module "./components/Navigation" {
  import React from "react";
  interface NavigationProps {
    onLogoClick: () => void;
  }
  const Navigation: React.FC<NavigationProps>;
  export default Navigation;
}

declare module "./components/Hero" {
  import React from "react";
  const HeroSection: React.FC;
  export default HeroSection;
}

declare module "./components/Features" {
  import React from "react";
  const FeaturesSection: React.FC;
  export default FeaturesSection;
}

declare module "./components/HowItWorks" {
  import React from "react";
  const HowItWorksSection: React.FC;
  export default HowItWorksSection;
}

declare module "./components/Pricing" {
  import React from "react";
  const PricingSection: React.FC;
  export default PricingSection;
}

declare module "./components/Footer" {
  import React from "react";
  const FooterSection: React.FC;
  export default FooterSection;
}

declare module "./components/LifeChoiceForm" {
  import React from "react";
  import type { SimulationFormData } from "../types/simulation";

  interface LifeChoiceFormProps {
    onSubmit: (formData: SimulationFormData) => Promise<void>;
    isLoading: boolean;
  }
  const LifeChoiceForm: React.FC<LifeChoiceFormProps>;
  export default LifeChoiceForm;
}

declare module "./components/SimulationResults" {
  import React from "react";
  import type { SimulationResult } from "../types/api";

  interface SimulationResultsProps {
    simulation: SimulationResult;
    onNewSimulation: () => void;
  }
  const SimulationResults: React.FC<SimulationResultsProps>;
  export default SimulationResults;
}