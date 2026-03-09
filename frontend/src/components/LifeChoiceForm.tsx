import React, { useState } from "react";
import { motion } from "framer-motion";
import { useAuth, useClerk } from "@clerk/clerk-react";
import type { SimulationFormData, Choice, UserContextForm } from "../types/simulation";

interface LifeChoiceFormProps {
  onSubmit: (formData: SimulationFormData) => Promise<void>;
  isLoading: boolean;
}

const LifeChoiceForm: React.FC<LifeChoiceFormProps> = ({ onSubmit, isLoading }) => {
  const { isSignedIn } = useAuth();
  const { openSignIn } = useClerk();

  const [choiceA, setChoiceA] = useState<Choice>({ title: "", description: "", category: "career" });
  const [choiceB, setChoiceB] = useState<Choice>({ title: "", description: "", category: "career" });
  const [userContext, setUserContext] = useState<UserContextForm>({
    age: "", current_location: "", current_salary: "", education_level: "",
  });

  const categories = ["career", "location", "education", "relationship", "lifestyle"];

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (!isSignedIn) { openSignIn(); return; }

    const ctx: any = {
      ...userContext,
      age: userContext.age ? parseInt(userContext.age, 10) : null,
      current_salary: userContext.current_salary ? parseInt(userContext.current_salary, 10) : null,
    };
    Object.keys(ctx).forEach((k) => {
      if (ctx[k] === null || ctx[k] === "" || ctx[k] === undefined) delete ctx[k];
    });
    if (Object.keys(ctx).length === 0) ctx.age = null;

    const detect = (title: string, sel: string) => {
      const t = title.toLowerCase();
      if (["university","college","school","education"].some(w => t.includes(w))) return "education";
      if (["move","relocate","city","country"].some(w => t.includes(w))) return "location";
      return sel || "career";
    };

    onSubmit({
      choice_a: { title: choiceA.title, description: choiceA.description, category: detect(choiceA.title, choiceA.category) },
      choice_b: { title: choiceB.title, description: choiceB.description, category: detect(choiceB.title, choiceB.category) },
      user_context: ctx,
    });
  };

  const input = "w-full px-4 py-3 bg-white border-2 border-stone-300 rounded-xl text-sm text-stone-900 placeholder:text-stone-400 focus:outline-none focus:border-stone-900 focus:ring-2 focus:ring-stone-100 transition-colors";
  const select = "w-full px-4 py-3 bg-white border-2 border-stone-300 rounded-xl text-sm text-stone-900 focus:outline-none focus:border-stone-900 focus:ring-2 focus:ring-stone-100 transition-colors appearance-none cursor-pointer";

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="max-w-3xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h2 className="text-3xl sm:text-4xl font-bold text-stone-900 mb-2">
        Run a simulation
      </h2>
      <p className="text-stone-400 text-sm mb-12">
        Define two paths and your background. We'll do the rest.
      </p>

      {/* Context */}
      <div className="mb-12">
        <p className="text-xs tracking-widest uppercase text-stone-400 mb-6">Your background</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
          <input type="number" placeholder="Age" value={userContext.age}
            onChange={(e) => setUserContext({ ...userContext, age: e.target.value })} className={input} />
          <input type="text" placeholder="Location" value={userContext.current_location}
            onChange={(e) => setUserContext({ ...userContext, current_location: e.target.value })} className={input} />
          <input type="number" placeholder="Salary (optional)" value={userContext.current_salary}
            onChange={(e) => setUserContext({ ...userContext, current_salary: e.target.value })} className={input} />
          <select value={userContext.education_level}
            onChange={(e) => setUserContext({ ...userContext, education_level: e.target.value })} className={select}>
            <option value="">Education</option>
            <option value="high_school">High School</option>
            <option value="bachelors">Bachelor's</option>
            <option value="masters">Master's</option>
            <option value="phd">PhD</option>
          </select>
        </div>
      </div>

      {/* Paths */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
        <div>
          <div className="flex items-center gap-2 mb-6">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <p className="text-xs tracking-widest uppercase text-stone-400">Path A</p>
          </div>
          <input type="text" placeholder="Job title or life choice" value={choiceA.title}
            onChange={(e) => setChoiceA({ ...choiceA, title: e.target.value })} className={input} required />
          <textarea placeholder="Describe this path..." value={choiceA.description}
            onChange={(e) => setChoiceA({ ...choiceA, description: e.target.value })}
            className={`${input} resize-none h-20 mt-3`} required />
          <select value={choiceA.category} onChange={(e) => setChoiceA({ ...choiceA, category: e.target.value })}
            className={`${select} mt-3`}>
            {categories.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
          </select>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-6">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <p className="text-xs tracking-widest uppercase text-stone-400">Path B</p>
          </div>
          <input type="text" placeholder="Job title or life choice" value={choiceB.title}
            onChange={(e) => setChoiceB({ ...choiceB, title: e.target.value })} className={input} required />
          <textarea placeholder="Describe this path..." value={choiceB.description}
            onChange={(e) => setChoiceB({ ...choiceB, description: e.target.value })}
            className={`${input} resize-none h-20 mt-3`} required />
          <select value={choiceB.category} onChange={(e) => setChoiceB({ ...choiceB, category: e.target.value })}
            className={`${select} mt-3`}>
            {categories.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
          </select>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading || !choiceA.title || !choiceB.title}
        className={`w-full py-3.5 rounded-xl text-sm font-medium transition-colors ${
          isLoading || !choiceA.title || !choiceB.title
            ? "bg-stone-200 text-stone-500 border-2 border-stone-300 cursor-not-allowed"
            : "bg-stone-950 text-white hover:bg-stone-800 active:scale-[0.99]"
        }`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Running simulation...
          </span>
        ) : !isSignedIn ? (
          "Sign in to simulate"
        ) : (
          "Simulate"
        )}
      </button>
    </motion.form>
  );
};

export default LifeChoiceForm;
