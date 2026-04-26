// Core Models matching backend schemas

export type SessionStatus =
  | 'created'
  | 'jd_uploaded'
  | 'resume_uploaded'
  | 'analyzed'
  | 'assessing'
  | 'plan_generated'
  | 'completed';

export type GapCategory = 'STRONG' | 'MODERATE' | 'WEAK' | 'MISSING';

export interface SkillRequirement {
  name: string;
  importance: 'must_have' | 'nice_to_have';
  level: 'beginner' | 'intermediate' | 'advanced';
}

export interface JDData {
  company_name: string;
  role_title: string;
  industry: string;
  experience_required: string;
  required_skills: SkillRequirement[];
  summary: string;
}

export interface CandidateSkill {
  name: string;
  years_of_experience: number;
  level: 'beginner' | 'intermediate' | 'advanced';
  evidence: string[];
}

export interface ResumeData {
  candidate_name: string;
  email?: string;
  current_role?: string;
  total_experience_years: number;
  skills: CandidateSkill[];
  education: string[];
  summary: string;
}

export interface SkillAssessment {
  skill_name: string;
  jd_level: string;
  candidate_level: string;
  score: number;
  gap_category: GapCategory;
  evidence: string[];
  notes: string;
  is_adjacent: boolean;
}

export interface GapAnalysis {
  overall_match_score: number;
  skill_assessments: SkillAssessment[];
  strengths: string[];
  critical_gaps: string[];
  adjacent_skills: string[];
  recommended_focus_order: string[];
}

export interface Resource {
  type: 'youtube' | 'article' | 'course' | 'practice' | 'documentation' | 'other';
  title: string;
  url: string;
  description?: string;
}

export interface Topic {
  title: string;
  description: string;
  estimated_minutes: number;
  resources: Resource[];
}

export interface Module {
  title: string;
  description: string;
  topics: Topic[];
  estimated_hours: number;
}

export interface Course {
  skill_name: string;
  priority: number;
  gap_category: string;
  total_estimated_hours: number;
  why_important: string;
  modules: Module[];
}

export interface LearningPlan {
  total_estimated_hours: number;
  completion_timeline_weeks: number;
  courses: Course[];
}

export interface InterviewRound {
  round_number: number;
  round_type: string;
  description: string;
  key_topics: string[];
  preparation_tips: string[];
  resources: Resource[];
}

export interface InterviewPrep {
  company_name: string;
  role_title: string;
  total_rounds: number;
  typical_duration_weeks: string;
  rounds: InterviewRound[];
  general_tips: string[];
}

export interface Session {
  session_id: string;
  created_at: string;
  updated_at: string;
  status: SessionStatus;
  jd_data?: JDData;
  resume_data?: ResumeData;
  gap_analysis?: GapAnalysis;
  learning_plan?: LearningPlan;
  interview_prep?: InterviewPrep;
}

export interface ChatMessage {
  role: 'human' | 'ai' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
}
