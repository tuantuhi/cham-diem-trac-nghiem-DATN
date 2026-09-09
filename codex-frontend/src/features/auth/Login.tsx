import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import api from '../../api/axios';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/login', {
        username: values.username,
        password: values.password,
      });
      const auth = response.data.data;
      setAuth({ id: auth.id, username: auth.username, role: auth.role }, auth.token);
      message.success('Đăng nhập thành công');
      navigate('/dashboard');
    } catch (error) {
      message.error('Đăng nhập thất bại. Vui lòng kiểm tra lại tài khoản hoặc kết nối máy chủ.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-in fade-in zoom-in-95 duration-500">
      <div className="text-center mb-6">
        <h3 className="text-xl font-bold text-slate-800">Đăng nhập</h3>
        <p className="text-sm text-slate-500 mt-1">Vui lòng đăng nhập để vào hệ thống</p>
      </div>

      <Form
        name="login"
        initialValues={{ remember: true }}
        onFinish={onFinish}
        size="large"
        layout="vertical"
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: 'Vui lòng nhập Tên đăng nhập!' }]}
        >
          <Input 
            prefix={<UserOutlined className="text-slate-400 mr-2" />} 
            placeholder="Tên đăng nhập" 
            className="py-2.5 font-medium"
          />
        </Form.Item>
        <Form.Item
          name="password"
          rules={[{ required: true, message: 'Vui lòng nhập Mật khẩu!' }]}
        >
          <Input.Password
            prefix={<LockOutlined className="text-slate-400 mr-2" />}
            placeholder="Mật khẩu"
            className="py-2.5 font-medium"
          />
        </Form.Item>
        <Form.Item className="mt-4 mb-0">
          <Button 
            type="primary" 
            htmlType="submit" 
            className="h-11 w-full text-base font-bold" 
            loading={loading}
          >
            Đăng nhập
          </Button>
        </Form.Item>
      </Form>
      <div className="text-center text-sm font-medium text-slate-500 mt-6 pt-4 border-t border-slate-100">
        Chưa có tài khoản? <Link className="font-bold text-blue-600 hover:text-blue-700 ml-1" to="/register">Đăng ký ngay</Link>
      </div>
    </div>
  );
};

export default Login;
