import React from 'react';
import { Avatar, Button, Layout, Menu } from 'antd';
import { Outlet, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { BarChart3, ClipboardCheck, GraduationCap, LayoutDashboard, LogOut, CheckCircle } from 'lucide-react';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const { isAuthenticated, logout, user } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const isStudent = user?.role === 'ROLE_STUDENT';

  const menuItems = [
    {
      key: '/dashboard',
      icon: <LayoutDashboard size={20} />,
      label: 'Tổng quan',
    },
    ...(!isStudent ? [
      {
        key: '/exams',
        icon: <ClipboardCheck size={20} />,
        label: 'Quản lý kỳ thi',
      },
      {
        key: '/students',
        icon: <GraduationCap size={20} />,
        label: 'Danh sách sinh viên',
      }
    ] : []),
    {
      key: '/results',
      icon: <BarChart3 size={20} />,
      label: 'Kết quả chấm thi',
    }
  ];

  return (
    <Layout className="min-h-screen bg-slate-50 relative">
      <Sider 
        breakpoint="lg" 
        collapsedWidth="0" 
        width={260} 
        className="h-screen sticky top-0 z-20 shadow-xl"
        style={{ backgroundColor: '#0f172a' }}
      >
        <div className="flex h-16 items-center gap-3 px-6 text-white border-b border-slate-800/60">
          <div className="flex items-center justify-center text-blue-500">
            <CheckCircle size={24} />
          </div>
          <div>
            <div className="text-lg font-bold tracking-wide text-white">AutoGrade</div>
          </div>
        </div>
        <div className="p-3 mt-2">
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            onClick={handleMenuClick}
            items={menuItems}
            style={{ backgroundColor: 'transparent' }}
          />
        </div>
      </Sider>

      <Layout className="min-h-screen flex flex-col bg-slate-50 transition-all duration-300">
        <Header className="z-10 flex h-16 items-center justify-between border-b border-slate-200 sticky top-0" style={{ backgroundColor: '#ffffff', padding: '0 32px' }}>
          <div className="flex items-center gap-3">
            <div className="text-base font-semibold text-slate-800">Hệ thống Chấm thi AutoGrade</div>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <Avatar className="bg-blue-100 text-blue-600 font-bold">
                {(user?.username || 'U').slice(0, 1).toUpperCase()}
              </Avatar>
              <div className="hidden text-right sm:block">
                <div className="text-sm font-bold text-slate-700 leading-none">{user?.username || 'Người dùng'}</div>
                <div className="text-xs font-medium text-slate-500 mt-1">
                  {user?.role === 'ROLE_TEACHER' ? 'Giáo viên' : user?.role === 'ROLE_STUDENT' ? 'Sinh viên' : 'Quản trị viên'}
                </div>
              </div>
            </div>
            <Button
              type="text"
              className="flex items-center gap-2 text-slate-600 hover:text-rose-600 hover:bg-rose-50 font-semibold px-3 py-1.5 rounded-md"
              icon={<LogOut size={16} />}
              onClick={() => {
                logout();
                navigate('/login');
              }}
            >
              Đăng xuất
            </Button>
          </div>
        </Header>
        
        <Content className="p-8 w-full flex-1 overflow-y-auto">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
