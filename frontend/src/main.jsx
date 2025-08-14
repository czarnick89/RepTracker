import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import router from "./router";
import "./index.css";
import { AuthProvider } from "./contexts/AuthContext";

createRoot(document.getElementById("root")).render(
  // Wrap the app in AuthProvider to give all components access to auth state/hooks
  <AuthProvider>
    <RouterProvider router={router} />
  </AuthProvider>
);
