import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const AuthLayout: React.FC = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-[#f6f7f4] px-4 py-10 text-slate-950">
      <div className="mx-auto grid min-h-[calc(100vh-5rem)] w-full max-w-6xl items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="hidden lg:block">
          <div className="inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-sm text-slate-600 shadow-sm">
            Chấm điểm trắc nghiệm tự động
          </div>
          <h1 className="mt-6 max-w-xl text-5xl font-semibold leading-tight tracking-normal">
            AutoGrade là hệ thống chấm điểm trắc nghiệm tự động nhanh chóng và chính xác.
          </h1>
          <div className="mt-8 grid max-w-xl grid-cols-3 gap-3">
            {['Tải lên', 'Nhận diện', 'Chấm điểm'].map((item) => (
              <div key={item} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <div className="text-sm font-medium text-slate-500">{item}</div>
                <div className="mt-3 h-1.5 rounded-full bg-slate-900" />
              </div>
            ))}
          </div>
        </section>
        <div className="mx-auto w-full max-w-md">
          <div className="mb-6">
            <div className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">AutoGrade</div>
            <h2 className="mt-2 text-3xl font-semibold">Hệ thống chấm điểm</h2>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
          <Outlet />
        </div>
      </div>
      </div>
    </div>
  );
};

export default AuthLayout;
