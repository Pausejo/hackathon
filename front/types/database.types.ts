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
        };
      };
    };
  };
};
