// Optional sign-in with Supabase Auth (magic link). If the two env vars are missing, the app works exactly as before.
// The anon key is PUBLIC by design. Data safety comes from the backend, which holds the service key.
const URL = import.meta.env.VITE_SUPABASE_URL;
const KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;
export const authEnabled = Boolean(URL && KEY);

let client = null;
async function getClient() {
  if (!authEnabled) return null;
  if (!client) {
    const { createClient } = await import("@supabase/supabase-js");
    client = createClient(URL, KEY, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } });
  }
  return client;
}

export async function getToken() {
  try {
    const c = await getClient();
    if (!c) return null;
    const { data } = await c.auth.getSession();
    return data.session?.access_token || null;
  } catch { return null; }
}

export async function signInWithEmail(email) {
  const c = await getClient();
  if (!c) throw new Error("Sign-in is not configured.");
  const { error } = await c.auth.signInWithOtp({ email, options: { emailRedirectTo: window.location.origin } });
  if (error) throw new Error(error.message);
}

export async function signOut() {
  const c = await getClient();
  if (c) await c.auth.signOut();
}

// Calls cb(session|null) now and on every change. Returns an unsubscribe function.
export function watchSession(cb) {
  let off = () => {};
  let dead = false;
  getClient().then((c) => {
    if (!c || dead) return;
    c.auth.getSession().then(({ data }) => !dead && cb(data.session));
    const { data } = c.auth.onAuthStateChange((_e, s) => cb(s));
    off = () => data.subscription.unsubscribe();
  }).catch(() => {});
  return () => { dead = true; off(); };
}
