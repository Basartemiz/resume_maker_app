import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Enterence from "./pages/enterence.jsx";
import TemplateStudio from "./pages/fill_form.jsx";
import Login from "./pages/Login.jsx";
import "./App.css";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 p-6">
        <Routes>
          <Route path="/" element={<Enterence />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/fill"
            element={
              <ProtectedRoute>
                <TemplateStudio />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
