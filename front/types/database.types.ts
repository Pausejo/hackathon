export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export type Database = {
  public: {
    Tables: {
      agents: {
        Row: {
          id: string;
          created_at: string;
          description: string;
          url: string;
          is_enabled: boolean;
          usage_count: number;
          success_rate: number;
        };
      };
      actions: {
        Row: {
          id: string;
          created_at: string;
          type: string;
          action: string;
        };
      };
      agent_actions: {
        Row: {
          id: string;
          created_at: string;
          agent_id: string;
          action_id: string;
        };
      };
      threads: {
        Row: {
          id: string;
          created_at: string;
          conversation_history: Json[];
        };
      };
    };
  };
};
