import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute role="PATIENT" />}>
        <Route
          path="/patient"
          element={<Dashboard title="Patient Dashboard" />}
        />
      </Route>

      <Route element={<ProtectedRoute role="DOCTOR" />}>
        <Route
          path="/doctor"
          element={<Dashboard title="Doctor Dashboard" />}
        />
      </Route>

      <Route element={<ProtectedRoute role="ADMIN" />}>
        <Route path="/admin" element={<Dashboard title="Admin Dashboard" />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
