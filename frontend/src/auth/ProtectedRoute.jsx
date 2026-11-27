import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { ROLE_HOME } from "./roles";

export default function ProtectedRoute({ role }) {
  const { user, loading } = useAuth();

  if (loading) return <p className="p-8 text-slate-500">Loading...</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role)
    return <Navigate to={ROLE_HOME[user.role]} replace />;

  return <Outlet />;
}
