// import "./App.css";
// import { BrowserRouter, Routes, Route } from "react-router-dom";
// import Login from "./pages/Login";
// import Register from "./pages/Register";
// import Landing from "./pages/Landing";
// import Dashboard from "./pages/Dashboard";
// import Profile from "./pages/Profile";
// import Logout from "./pages/Logout";
// import ForgotPassword from "./pages/ForgotPassword";
// import PrivateRoute from "./components/PrivateRoute";
// import ResetPassword from "./pages/ResetPassword";
// import NotFound from "./pages/NotFound";
// import { AuthProvider } from "./contexts/AuthContext";
// import Layout from "./components/Layout";

// function App() {
//   return (
//     <AuthProvider>
//       <BrowserRouter>
//         <Routes>
//           {/* Public routes */}
//           <Route path="/" element={<Landing />} />
//           <Route path="/login" element={<Login />} />
//           <Route path="/logout" element={<Logout />} />
//           <Route path="/register" element={<Register />} />
//           <Route path="/forgot-password" element={<ForgotPassword />} />
//           <Route
//             path="/reset-password/:uid/:token"
//             element={<ResetPassword />}
//           />

//           {/* Protected routes */}
//           <Route
//             path="/dashboard"
//             element={
//               <PrivateRoute>
//                 <Layout>
//                   <Dashboard />
//                 </Layout>
//               </PrivateRoute>
//             }
//           />
//           <Route
//             path="/profile"
//             element={
//               <PrivateRoute>
//                 <Layout>
//                   <Profile />
//                 </Layout>
//               </PrivateRoute>
//             }
//           />

//           {/* Catch-all */}
//           <Route path="*" element={<NotFound />} />
//         </Routes>
//       </BrowserRouter>
//     </AuthProvider>
//   );
// }

// export default App;
