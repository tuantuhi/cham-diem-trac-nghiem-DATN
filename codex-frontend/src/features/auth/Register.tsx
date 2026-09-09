import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import api from '../../api/axios';

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await api.post('/auth/register', {
        username: values.username,
        password: values.password,
      });
      message.success('Đăng ký thành công. Vui lòng đăng nhập.');
      navigate('/login');
    } catch (error) {
      message.error('Đăng ký thất bại. Tên tài khoản có thể đã tồn tại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-in fade-in zoom-in-95 duration-500">
      <div className="text-center mb-6">
        <h3 className="text-xl font-bold text-slate-800">Đăng ký tài khoản</h3>
        <p className="text-sm text-slate-500 mt-1">Tạo tài khoản mới để bắt đầu chấm điểm</p>
      </div>

      <Form
        name="register"
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
            Đăng ký
          </Button>
        </Form.Item>
      </Form>
      <div className="text-center text-sm font-medium text-slate-500 mt-6 pt-4 border-t border-slate-100">
        Đã có tài khoản? <Link className="font-bold text-blue-600 hover:text-blue-700 ml-1" to="/login">Đăng nhập tại đây</Link>
      </div>
    </div>
  );
};

export default Register;
