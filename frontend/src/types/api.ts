export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

export interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

export interface LifeChoice {
  title: string;
  description: string;
  category: string;
}

export interface UserContext {
  age?: string | number | null;
  current_location?: string;
  current_salary?: string | number | null;
  education_level?: string;
}

export interface SimulationData {
  choice_a: LifeChoice;
  choice_b: LifeChoice;
  user_context?: UserContext;
}

export interface TimelineEvent {
  year: number;
  event: string;
  impact_score: number;
}

export interface TimelinePoint {
  year: number;
  salary?: number;
  happiness_score: number;
  major_event?: string;
  location?: string;
  career_title?: string;
}

export interface SimulationResult {
  id: string;
  choice_a_timeline: TimelinePoint[];
  choice_b_timeline: TimelinePoint[];
  summary: string;
  created_at: string;
}

export interface UserData {
  id: string;
  email?: string;
  firstName?: string;
  lastName?: string;
}

export interface PaymentData {
  priceId: string;
  successUrl?: string;
  cancelUrl?: string;
}