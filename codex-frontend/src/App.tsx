import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import AuthLayout from './layouts/AuthLayout';
import MainLayout from './layouts/MainLayout';
import Login from './features/auth/Login';
import Register from './features/auth/Register';
import { useAuthStore } from './store/authStore';

import Dashboard from './features/dashboard/Dashboard';
import Exams from './features/exam/Exams';
import ExamDetails from './features/exam/ExamDetails';
import Students from './features/student/Students';
import Results from './features/result/Results';

function App() {
  const { user } = useAuthStore();
  const isStudent = user?.role === 'ROLE_STUDENT';

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1677ff', // Academic Blue
          colorInfo: '#1677ff',
          colorSuccess: '#10b981',
          colorWarning: '#f59e0b',
          colorError: '#ef4444',
          borderRadius: 8,
          wireframe: false,
          fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        },
        components: {
          Button: {
            controlHeight: 40,
            borderRadius: 8,
            fontWeight: 500,
          },
          Card: {
            borderRadiusLG: 8,
            boxShadowTertiary: '0 10px 15px -3px rgba(0,0,0,0.02), 0 4px 6px -4px rgba(0,0,0,0.02)',
          },
        }
      }}
    >
      <BrowserRouter>
        <Routes>
          {/* Auth Routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Protected Routes */}
          <Route element={<MainLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            {!isStudent && (
              <>
                <Route path="/exams" element={<Exams />} />
                <Route path="/exams/:id" element={<ExamDetails />} />
                <Route path="/students" element={<Students />} />
              </>
            )}
            <Route path="/results" element={<Results />} />
          </Route>

          {/* Redirect root to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
