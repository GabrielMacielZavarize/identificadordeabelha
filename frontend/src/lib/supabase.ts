import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined

// Sem as variáveis configuradas exporta null — autenticação desabilitada localmente.
// Quando VITE_SUPABASE_URL e VITE_SUPABASE_ANON_KEY forem definidas o cliente é criado normalmente.
export const supabase = (supabaseUrl && supabaseAnonKey)
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null
