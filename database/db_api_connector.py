from supabase import create_client, Client


class DBAPIConnector:
    supabase: Client

    def connect(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
