import { createBrowserRouter } from "react-router-dom";

// Components controlling route layouts and access
import PrivateRoute from "./components/PrivateRoute";  // Protects routes that require login
import Layout from "./components/Layout";              // Layout for authenticated users
import PublicLayout from "./components/PublicLayout";  // Layout for unauthenticated users

// Page components
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Logout from "./pages/Logout";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

const router = createBrowserRouter([
  // Public routes (no login required)
  {
    path: "/",
    element: <PublicLayout />,
    children: [
      { index: true, element: <Landing /> },
      { path: "login", element: <Login /> },
      { path: "register", element: <Register /> },
      { path: "logout", element: <Logout /> },
      { path: "forgot-password", element: <ForgotPassword /> },
      { path: "reset-password/:uid/:token", element: <ResetPassword /> }, 
    ],
  },

  // Private routes (login required)
  {
    path: "/",
    element: (
      <PrivateRoute>
         <Layout />  {/*Wrap private pages in Layout for nav/sidebar, etc. */}
      </PrivateRoute>
    ),
    children: [
      { path: "dashboard", element: <Dashboard /> },
      { path: "profile", element: <Profile /> },
    ],
  },

  // Catch-all for unmatched routes
  { path: "*", element: <NotFound /> },
]);

export default router;