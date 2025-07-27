import React, { useState } from 'react';
import { motion } from 'framer-motion';

const LifeChoiceForm = ({ onSubmit, isLoading }) => {
  const [choiceA, setChoiceA] = useState({
    title: '',
    description: '',
    category: 'career'
  });
  
  const [choiceB, setChoiceB] = useState({
    title: '',
    description: '',
    category: 'career'
  });
  
  const [userContext, setUserContext] = useState({
    age: '',
    current_location: '',
    current_salary: '',
    education_level: ''
  });
  
  const categories = ['career', 'location', 'education', 'relationship', 'lifestyle'];
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      choice_a: choiceA,
      choice_b: choiceB,
      user_context: userContext
    });
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
            onChange={(e) => setUserContext({...userContext, age: e.target.value})}
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="text"
            placeholder="Current location"
            value={userContext.current_location}
            onChange={(e) => setUserContext({...userContext, current_location: e.target.value})}
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="number"
            placeholder="Current salary (optional)"
            value={userContext.current_salary}
            onChange={(e) => setUserContext({...userContext, current_salary: e.target.value})}
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <select
            value={userContext.education_level}
            onChange={(e) => setUserContext({...userContext, education_level: e.target.value})}
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
            onChange={(e) => setChoiceA({...choiceA, title: e.target.value})}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <textarea
            placeholder="Describe this path in detail..."
            value={choiceA.description}
            onChange={(e) => setChoiceA({...choiceA, description: e.target.value})}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg h-24 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <select
            value={choiceA.category}
            onChange={(e) => setChoiceA({...choiceA, category: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
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
            onChange={(e) => setChoiceB({...choiceB, title: e.target.value})}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
          <textarea
            placeholder="Describe this path in detail..."
            value={choiceB.description}
            onChange={(e) => setChoiceB({...choiceB, description: e.target.value})}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg h-24 resize-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
          <select
            value={choiceB.category}
            onChange={(e) => setChoiceB({...choiceB, category: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
        </motion.div>
      </div>
      
      <motion.button
        type="submit"
        disabled={isLoading || !choiceA.title || !choiceB.title}
        className={`w-full mt-8 py-4 px-6 rounded-xl text-white font-semibold text-lg transition-all duration-300 ${
          isLoading || !choiceA.title || !choiceB.title
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
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
          'Simulate My Life Paths'
        )}
      </motion.button>
    </motion.form>
  );
};

export default LifeChoiceForm;