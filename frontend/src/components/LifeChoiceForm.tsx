import React, { useState } from "react";
import { motion } from "framer-motion";
import type { SimulationFormData, Choice, UserContextForm } from "../types/simulation";

interface LifeChoiceFormProps {
  onSubmit: (formData: SimulationFormData) => Promise<void>;
  isLoading: boolean;
}

const LifeChoiceForm: React.FC<LifeChoiceFormProps> = ({ onSubmit, isLoading }) => {
  const [choiceA, setChoiceA] = useState<Choice>({
    title: "",
    description: "",
    category: "career",
  });

  const [choiceB, setChoiceB] = useState<Choice>({
    title: "",
    description: "",
    category: "career",
  });

  const [userContext, setUserContext] = useState<UserContextForm>({
    age: "",
    current_location: "",
    current_salary: "",
    education_level: "",
  });

  const categories: string[] = [
    "career",
    "location",
    "education",
    "relationship",
    "lifestyle",
  ];

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();

    // Debug: Log the raw form state
    console.log("🔍 Form state debug:");
    console.log("choiceA:", choiceA);
    console.log("choiceB:", choiceB);
    console.log("userContext:", userContext);

    // Transform user context data to ensure proper types
    const transformedUserContext: any = {
      ...userContext,
      // Convert age to integer if provided, otherwise keep as null/empty
      age: userContext.age ? parseInt(userContext.age, 10) : null,
      // Convert salary to integer if provided, otherwise keep as null/empty
      current_salary: userContext.current_salary
        ? parseInt(userContext.current_salary, 10)
        : null,
    };

    // Clean up empty values but ensure user_context is never completely empty
    Object.keys(transformedUserContext).forEach((key) => {
      if (
        transformedUserContext[key] === null ||
        transformedUserContext[key] === "" ||
        transformedUserContext[key] === undefined
      ) {
        delete transformedUserContext[key];
      }
    });

    // Ensure user_context always has at least one field to prevent empty object issues
    if (Object.keys(transformedUserContext).length === 0) {
      transformedUserContext.age = null;
    }

    // Auto-detect categories for better UX
    const detectCategory = (title: string, selectedCategory: string): string => {
      const titleLower = title.toLowerCase();
      if (
        titleLower.includes("university") ||
        titleLower.includes("college") ||
        titleLower.includes("school") ||
        titleLower.includes("education")
      ) {
        return "education";
      }
      if (
        titleLower.includes("move") ||
        titleLower.includes("relocate") ||
        titleLower.includes("city") ||
        titleLower.includes("country")
      ) {
        return "location";
      }
      return selectedCategory || "career"; // Default to career if not detected
    };

    // Ensure clean data structure
    const cleanedData: SimulationFormData = {
      choice_a: {
        title: choiceA.title || "",
        description: choiceA.description || "",
        category: detectCategory(choiceA.title, choiceA.category),
      },
      choice_b: {
        title: choiceB.title || "",
        description: choiceB.description || "",
        category: detectCategory(choiceB.title, choiceB.category),
      },
      user_context: transformedUserContext,
    };

    console.log("🧹 Cleaned data being sent:", cleanedData);
    onSubmit(cleanedData);
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="bg-white rounded-2xl shadow-xl p-8 max-w-4xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">
        Compare Your Life Paths
      </h2>

      {/* User Context */}
      <div className="mb-8 p-6 bg-gray-50 rounded-xl">
        <h3 className="text-xl font-semibold mb-4">About You</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="number"
            placeholder="Your age"
            value={userContext.age}
            onChange={(e) =>
              setUserContext({ ...userContext, age: e.target.value })
            }
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="text"
            placeholder="Current location"
            value={userContext.current_location}
            onChange={(e) =>
              setUserContext({
                ...userContext,
                current_location: e.target.value,
              })
            }
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="number"
            placeholder="Current salary (optional)"
            value={userContext.current_salary}
            onChange={(e) =>
              setUserContext({ ...userContext, current_salary: e.target.value })
            }
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <select
            value={userContext.education_level}
            onChange={(e) =>
              setUserContext({
                ...userContext,
                education_level: e.target.value,
              })
            }
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Education level</option>
            <option value="high_school">High School</option>
            <option value="bachelors">Bachelor's Degree</option>
            <option value="masters">Master's Degree</option>
            <option value="phd">PhD</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Choice A */}
        <motion.div
          className="p-6 border-2 border-blue-200 rounded-xl bg-blue-50"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <h3 className="text-xl font-semibold text-blue-800 mb-4">Path A</h3>
          <input
            type="text"
            placeholder="e.g., Become a Software Engineer"
            value={choiceA.title}
            onChange={(e) => setChoiceA({ ...choiceA, title: e.target.value })}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <textarea
            placeholder="Describe this path in detail..."
            value={choiceA.description}
            onChange={(e) =>
              setChoiceA({ ...choiceA, description: e.target.value })
            }
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg h-24 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <select
            value={choiceA.category}
            onChange={(e) =>
              setChoiceA({ ...choiceA, category: e.target.value })
            }
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>
        </motion.div>

        {/* Choice B */}
        <motion.div
          className="p-6 border-2 border-green-200 rounded-xl bg-green-50"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <h3 className="text-xl font-semibold text-green-800 mb-4">Path B</h3>
          <input
            type="text"
            placeholder="e.g., Start my own business"
            value={choiceB.title}
            onChange={(e) => setChoiceB({ ...choiceB, title: e.target.value })}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
          <textarea
            placeholder="Describe this path in detail..."
            value={choiceB.description}
            onChange={(e) =>
              setChoiceB({ ...choiceB, description: e.target.value })
            }
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg h-24 resize-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
          <select
            value={choiceB.category}
            onChange={(e) =>
              setChoiceB({ ...choiceB, category: e.target.value })
            }
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>
        </motion.div>
      </div>

      <motion.button
        type="submit"
        disabled={isLoading || !choiceA.title || !choiceB.title}
        className={`w-full mt-8 py-4 px-6 rounded-xl text-white font-semibold text-lg transition-all duration-300 ${
          isLoading || !choiceA.title || !choiceB.title
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl"
        }`}
        whileHover={!isLoading ? { scale: 1.02 } : {}}
        whileTap={!isLoading ? { scale: 0.98 } : {}}
      >
        {isLoading ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
            Generating Your Future...
          </div>
        ) : (
          "Simulate My Life Paths"
        )}
      </motion.button>
    </motion.form>
  );
};

export default LifeChoiceForm;