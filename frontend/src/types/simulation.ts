export interface Choice {
  title: string;
  description: string;
  category: string;
}

export interface UserContextForm {
  age: string;
  current_location: string;
  current_salary: string;
  education_level: string;
}

export interface SimulationFormData {
  choice_a: Choice;
  choice_b: Choice;
  user_context: UserContextForm;
}