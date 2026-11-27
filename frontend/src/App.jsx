import { useEffect, useState } from "react";
import axios from "axios";

export default function App() {
  const [status, setStatus] = useState("Checking the API...");

  useEffect(() => {
    axios
      .get("/api/auth/csrf/")
      .then(() => setStatus("Connected to the Django API"))
      .catch(() => setStatus("Cannot reach the API. Is Django running?"));
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="bg-white p-8 rounded-xl shadow text-center">
        <h1 className="text-2xl font-bold text-blue-700">
          Hospital Management System
        </h1>
        <p className="mt-3 text-slate-600">{status}</p>
      </div>
    </div>
  );
}
