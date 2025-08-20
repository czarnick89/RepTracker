import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../api/axiosRefreshInterceptor";

export default function GoogleCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state"); 

    if (code && state) {
      api
        .post(
          `${
            import.meta.env.VITE_BACKEND_URL
          }/api/v1/workouts/google-calendar/oauth2callback/`,
          { code, state },
        )
        .then((res) => {
          console.log("Callback success:", res.data);
          navigate("/profile");
        })
        .catch((err) => {
          console.error(
            "Callback failed:",
            err.response?.data || err.message
          );
        });
    }
  }, [searchParams, navigate]);

  return <div>Linking Google Calendar...</div>;
}
