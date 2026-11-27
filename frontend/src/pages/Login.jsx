import { useState } from "react";
import { Navigate, useNavigate,Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ROLE_HOME } from "../auth/roles";



export default function Login() {
  const { user, loading, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (loading) return <p className="p-8 text-slate-500">Loading...</p>;
  if (user) return <Navigate to={ROLE_HOME[user.role]} replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const loggedIn = await login(email, password);
      navigate(ROLE_HOME[loggedIn.role], { replace: true });
    } catch (err) {
      const status = err.response?.status;
      if (status === 401) setError("Incorrect email or password.");
      else if (status === 429)
        setError("Too many attempts. Please wait a minute.");
      else setError("Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm bg-white p-8 rounded-xl shadow space-y-4"
      >
        <h1 className="text-2xl font-bold text-blue-700 text-center">
          Hospital Management
        </h1>
        <p className="text-center text-slate-500 text-sm">
          Sign in to your account
        </p>

        {error && (
          <div className="bg-red-50 text-red-700 text-sm p-3 rounded">
            {error}
          </div>
        )}

        <div>
          <label
            className="block text-sm font-medium text-slate-700 mb-1"
            htmlFor="email"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-slate-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label
            className="block text-sm font-medium text-slate-700 mb-1"
            htmlFor="password"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-slate-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-medium py-2 rounded"
        >
          {submitting ? "Signing in..." : "Sign in"}
        </button>
        <p className="text-center text-sm text-slate-600">
          New patient?{" "}
          <Link to="/register" className="text-blue-600 hover:underline">
            Create an account
          </Link>
        </p>
      </form>
    </div>
  );
}
