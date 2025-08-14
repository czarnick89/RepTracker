import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

// Component to protect routes that require authentication
export default function PrivateRoute({ children }) {
  const { user, loading } = useAuth(); // Get current user and loading state from AuthContext
  const location = useLocation(); // Get current location to redirect back after login

  if (loading) return <div>Loading...</div>;

  // If user is not logged in, redirect to login page
  // `state.from` keeps track of original route to redirect after successful login
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;

  // If user is logged in, render the protected children components
  return children;
}
