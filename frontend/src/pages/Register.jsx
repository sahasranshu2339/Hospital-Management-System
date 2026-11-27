import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { ROLE_HOME } from "../auth/roles";

const EMPTY = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  password: "",
};

export default function Register() {
  const { user, loading, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  if (loading) return <p className="p-8 text-slate-500">Loading...</p>;
  if (user) return <Navigate to={ROLE_HOME[user.role]} replace />;

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErrors({});
    setSubmitting(true);
    try {
      await api.post("/auth/register/", form);
      // Account created: sign them in straight away.
      const loggedIn = await login(form.email, form.password);
      navigate(ROLE_HOME[loggedIn.role], { replace: true });
    } catch (err) {
      const status = err.response?.status;
      if (status === 400) setErrors(err.response.data);
      else if (status === 429)
        setErrors({ general: ["Too many attempts. Please try again later."] });
      else setErrors({ general: ["Something went wrong. Please try again."] });
    } finally {
      setSubmitting(false);
    }
  }

  function field(name, label, type = "text", extra = {}) {
    return (
      <div>
        <label
          className="block text-sm font-medium text-slate-700 mb-1"
          htmlFor={name}
        >
          {label}
        </label>
        <input
          id={name}
          type={type}
          value={form[name]}
          onChange={update(name)}
          className="w-full border border-slate-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          {...extra}
        />
        {errors[name] && (
          <ul className="mt-1 text-sm text-red-600 list-disc list-inside">
            {[].concat(errors[name]).map((msg, i) => (
              <li key={i}>{msg}</li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4 py-8">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm bg-white p-8 rounded-xl shadow space-y-4"
      >
        <h1 className="text-2xl font-bold text-blue-700 text-center">
          Create your account
        </h1>
        <p className="text-center text-slate-500 text-sm">
          Patient registration
        </p>

        {(errors.general || errors.non_field_errors) && (
          <div className="bg-red-50 text-red-700 text-sm p-3 rounded">
            {[].concat(errors.general || errors.non_field_errors).join(" ")}
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          {field("first_name", "First name", "text", {
            required: true,
            autoComplete: "given-name",
          })}
          {field("last_name", "Last name", "text", {
            required: true,
            autoComplete: "family-name",
          })}
        </div>
        {field("email", "Email", "email", {
          required: true,
          autoComplete: "email",
        })}
        {field("phone", "Phone (optional)", "tel", { autoComplete: "tel" })}
        {field("password", "Password", "password", {
          required: true,
          autoComplete: "new-password",
          minLength: 10,
        })}
        <p className="text-xs text-slate-500">
          At least 10 characters. Avoid common passwords.
        </p>

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-medium py-2 rounded"
        >
          {submitting ? "Creating account..." : "Create account"}
        </button>

        <p className="text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  );
}
