import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axiosRefreshInterceptor';

export default function ResetPassword() {
  const { uid, token } = useParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== passwordConfirm) {
      setStatus('error');
      setMessage('Passwords do not match.');
      return;
    }

    try {
      const res = await api.post(
        `https://127.0.0.1:8000/api/v1/users/password-reset-confirm/${uid}/${token}/`,
        { password },
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      );

      setStatus('success');
      setMessage('Password reset successfully. Redirecting to login...');
      setTimeout(() => navigate('/login'), 3000);
    } catch (err) {
      const error =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Something went wrong. Please try again.';
      setStatus('error');
      setMessage(Array.isArray(error) ? error.join(' ') : error);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '2rem auto' }}>
      <h2>Reset Password</h2>

      {status && (
        <p style={{ color: status === 'success' ? 'green' : 'red' }}>{message}</p>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="password">New Password:</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="passwordConfirm">Confirm Password:</label>
          <input
            id="passwordConfirm"
            type="password"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>

        <button
          type="submit"
          style={{
            padding: '0.5rem 1rem',
            marginBottom: '1rem',
            cursor: 'pointer',
          }}
        >
          Reset Password
        </button>
      </form>
    </div>
  );
}
