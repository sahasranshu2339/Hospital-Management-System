import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Dashboard({ title }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white shadow px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-blue-700">{title}</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-600">
            {user.email} ({user.role})
          </span>
          <button
            onClick={handleLogout}
            className="text-sm bg-slate-200 hover:bg-slate-300 px-3 py-1 rounded"
          >
            Log out
          </button>
        </div>
      </header>
      <main className="p-6 text-slate-600">Content coming soon.</main>
    </div>
  );
}
