export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  researchData?: any;
  sources?: Array<{
    title: string;
    url?: string;
  }>;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  research_data?: any;
  sources?: Array<{
    title: string;
    url?: string;
  }>;
}
