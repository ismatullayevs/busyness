import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const apiBase = import.meta.env.VITE_API_URL || '';
      const endpoint = apiBase + (isRegistering ? '/api/auth/register' : '/api/auth/login');
      const body = isRegistering 
        ? JSON.stringify({ email, password })
        : new URLSearchParams({ username: email, password });

      const headers: HeadersInit = isRegistering 
        ? { 'Content-Type': 'application/json' }
        : { 'Content-Type': 'application/x-www-form-urlencoded' };

      const res = await fetch(endpoint, {
        method: 'POST',
        headers,
        body,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Authentication failed');
      }

      if (isRegistering) {
        // After registration, log in automatically
        const loginRes = await fetch(apiBase + '/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ username: email, password }),
        });
        const loginData = await loginRes.json();
        login(loginData.access_token);
      } else {
        const data = await res.json();
        login(data.access_token);
      }
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container" style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      padding: 'var(--spacing-md)'
    }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
        <h1 style={{ textAlign: 'center', marginBottom: 'var(--spacing-lg)' }}>
          {isRegistering ? 'Create Account' : 'Welcome Back'}
        </h1>
        
        {error && (
          <div className="text-danger mb-md" style={{ textAlign: 'center' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleEmailAuth} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input 
              type="email" 
              className="form-input" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="form-input" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading}
          >
            {loading ? 'Processing...' : (isRegistering ? 'Sign Up' : 'Log In')}
          </button>
        </form>

        <div className="divider" style={{ margin: 'var(--spacing-lg) 0', textAlign: 'center', opacity: 0.5 }}>
          OR
        </div>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <GoogleLogin
            onSuccess={async (credentialResponse) => {
              try {
                setLoading(true);
                const apiBase = import.meta.env.VITE_API_URL || '';
                const res = await fetch(apiBase + '/api/auth/google', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ token: credentialResponse.credential }),
                });
                
                if (!res.ok) throw new Error('Google authentication failed');
                
                const data = await res.json();
                login(data.access_token);
                navigate('/');
              } catch (err) {
                setError('Google login failed');
              } finally {
                setLoading(false);
              }
            }}
            onError={() => setError('Google login failed')}
            useOneTap
            theme="filled_black"
            shape="pill"
          />
        </div>

        <p style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
          {isRegistering ? 'Already have an account?' : "Don't have an account?"}
          {' '}
          <button 
            className="btn-link" 
            onClick={() => setIsRegistering(!isRegistering)}
            style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', padding: 0 }}
          >
            {isRegistering ? 'Log In' : 'Sign Up'}
          </button>
        </p>
      </div>
    </div>
  );
}
