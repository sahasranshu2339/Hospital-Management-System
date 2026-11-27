import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  withCredentials: true, // send our login cookies
  xsrfCookieName: "csrftoken", // Django's CSRF cookie
  xsrfHeaderName: "X-CSRFToken", // header Django expects
});

// Axios reads the csrftoken cookie and adds the header for us.
// The cookie only exists after we have called /auth/csrf/ once.
export async function ensureCsrf() {
  await api.get("/auth/csrf/");
}

// ---- automatic token refresh ----
let refreshPromise = null;

function refreshAccessToken() {
  // If several requests fail at once, they all wait for ONE refresh call.
  if (!refreshPromise) {
    refreshPromise = api.post("/auth/refresh/").finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

const NO_REFRESH_URLS = [
  "/auth/login/",
  "/auth/refresh/",
  "/auth/register/",
  "/auth/logout/",
];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    const skip = NO_REFRESH_URLS.some((url) => original?.url?.includes(url));

    if (status === 401 && original && !original._retried && !skip) {
      original._retried = true;
      try {
        await refreshAccessToken();
        return api(original); // try the original request again
      } catch (refreshError) {
        // The refresh token is also invalid or expired: the user must log in again.
        window.dispatchEvent(new Event("auth:logout"));
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

export default api;
