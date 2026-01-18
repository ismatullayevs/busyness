import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/Home';
import Completed from './pages/Completed';
import Login from './pages/Login';

function RequireAuth({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function AuthenticatedApp() {
  const { logout } = useAuth();

  return (
    <div className="app-layout">
      <header className="header">
        <div className="container header-content">
          <NavLink to="/" className="logo">
            <span className="logo-icon">📊</span>
            <span>Busyness</span>
          </NavLink>
          <nav className="nav">
            <NavLink
              to="/"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              end
            >
              Active
            </NavLink>
            <NavLink
              to="/completed"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Completed
            </NavLink>
            <button 
              onClick={logout}
              className="btn btn-ghost"
              style={{ marginLeft: 'var(--spacing-md)' }}
            >
              Logout
            </button>
          </nav>
        </div>
      </header>
      <main className="main-content">
        <div className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/completed" element={<Completed />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <RequireAuth>
                <AuthenticatedApp />
              </RequireAuth>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
