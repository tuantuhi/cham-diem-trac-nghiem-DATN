import React, { useState } from 'react';
import { Button, Card, Drawer, Form, Input, Space, Table, message, Modal } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Upload } from 'lucide-react';
import * as XLSX from 'xlsx';
import { resources } from '../../api/resources';
import type { Student } from '../../api/resources';

const Students: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const students = useQuery({ queryKey: ['students'], queryFn: resources.students.list });

  const createStudent = useMutation({
    mutationFn: resources.students.create,
    onSuccess: () => {
      message.success('Đã lưu thông tin sinh viên thành công!');
      form.resetFields();
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ['students'] });
    },
  });

  const importStudents = useMutation({
    mutationFn: resources.students.import,
    onSuccess: (data) => {
      message.success(`Đã nhập thành công ${data.length} sinh viên từ file Excel!`);
      queryClient.invalidateQueries({ queryKey: ['students'] });
    },
  });

  const removeStudent = useMutation({
    mutationFn: resources.students.remove,
    onSuccess: () => {
      message.success('Đã xóa thông tin sinh viên thành công!');
      queryClient.invalidateQueries({ queryKey: ['students'] });
    },
  });

  const readWorkbook = async (file: File) => {
    try {
      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer);
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<Record<string, any>>(sheet);
      const payload = rows.map((row) => ({
        studentCode: String(row.studentCode || row.code || row['Student Code'] || row['Mã sinh viên'] || row['Mã SV'] || ''),
        fullName: String(row.fullName || row.name || row['Full Name'] || row['Họ và tên'] || row['Họ tên'] || ''),
        className: String(row.className || row.class || row['Class'] || row['Lớp'] || ''),
        email: String(row.email || row['Email'] || ''),
      }));
      importStudents.mutate(payload);
    } catch {
      message.error('Đọc file Excel thất bại. Vui lòng kiểm tra lại cấu trúc file.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">Danh sách sinh viên</h1>
          <p className="mt-1 text-sm text-slate-500">Quản lý danh sách sinh viên tham gia làm bài thi trắc nghiệm.</p>
        </div>
        <Space>
          <label className="inline-flex items-center justify-center px-4 h-10 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded cursor-pointer transition-colors shadow-sm text-sm">
            <Upload size={16} className="mr-2" />
            Nhập từ Excel
            <input
              hidden
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) readWorkbook(file);
                event.currentTarget.value = '';
              }}
            />
          </label>
          <Button type="primary" icon={<Plus size={16} />} onClick={() => setOpen(true)} className="h-10">
            Thêm sinh viên
          </Button>
        </Space>
      </div>

      <Table
        rowKey="id"
        loading={students.isLoading}
        dataSource={students.data ?? []}
        className="border border-slate-100/50 rounded-lg overflow-hidden"
        columns={[
          { title: 'Mã sinh viên', dataIndex: 'studentCode', render: (value?: string) => <span className="font-mono text-xs font-semibold text-slate-600">{value || '-'}</span> },
          { title: 'Họ và tên', render: (_, record: Student) => <span className="font-bold text-slate-800">{record.fullName || `${record.firstName || ''} ${record.lastName || ''}`.trim() || '-'}</span> },
          { title: 'Lớp học', dataIndex: 'className', render: (value?: string) => <span className="font-semibold text-slate-600">{value || '-'}</span> },
          { title: 'Email', dataIndex: 'email', render: (value?: string) => <span className="text-slate-600">{value || '-'}</span> },
          {
            title: 'Hành động',
            width: 96,
            render: (_, record: Student) => (
              <Button size="middle" danger icon={<Trash2 size={14} />} onClick={() => {
                Modal.confirm({
                  title: 'Xóa sinh viên này?',
                  content: 'Thông tin sinh viên và các bài nộp liên quan sẽ bị loại bỏ.',
                  okText: 'Xác nhận xóa',
                  okType: 'danger',
                  cancelText: 'Hủy',
                  onOk: () => removeStudent.mutate(record.id)
                });
              }} />
            ),
          },
        ]}
      />

      <Drawer title={<span className="font-bold text-slate-800">Thêm sinh viên mới</span>} open={open} onClose={() => setOpen(false)} width={420}>
        <Form layout="vertical" form={form} onFinish={(values) => createStudent.mutate(values)}>
          <Form.Item name="studentCode" label={<span className="font-bold text-slate-700">Mã sinh viên</span>} rules={[{ required: true, message: 'Mã sinh viên là bắt buộc' }]}>
            <Input size="large" placeholder="Ví dụ: 20224185" />
          </Form.Item>
          <Form.Item name="fullName" label={<span className="font-bold text-slate-700">Họ và tên</span>} rules={[{ required: true, message: 'Họ tên là bắt buộc' }]}>
            <Input size="large" placeholder="Ví dụ: Nguyễn Văn A" />
          </Form.Item>
          <Form.Item name="className" label={<span className="font-bold text-slate-700">Lớp học</span>}>
            <Input size="large" placeholder="Ví dụ: Điện tử 08" />
          </Form.Item>
          <Form.Item name="email" label={<span className="font-bold text-slate-700">Email</span>}>
            <Input size="large" type="email" placeholder="Ví dụ: sv@hust.edu.vn" />
          </Form.Item>
          <div className="pt-2">
            <Button type="primary" htmlType="submit" loading={createStudent.isPending} className="w-full h-10 font-bold">
              Lưu sinh viên
            </Button>
          </div>
        </Form>
      </Drawer>
    </div>
  );
};

export default Students;
