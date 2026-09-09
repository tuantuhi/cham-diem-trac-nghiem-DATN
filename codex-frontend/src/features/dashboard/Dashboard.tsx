import React from 'react';
import { Alert, Card, Col, Row, Skeleton, Table, Tag } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, ClipboardList, GraduationCap, UploadCloud } from 'lucide-react';
import { resources, getExamTypeLabel } from '../../api/resources';

const Dashboard: React.FC = () => {
  const exams = useQuery({ queryKey: ['exams'], queryFn: resources.exams.list });
  const students = useQuery({ queryKey: ['students'], queryFn: resources.students.list });
  const submissions = useQuery({ queryKey: ['submissions'], queryFn: resources.submissions.list });

  const done = submissions.data?.filter((item) => item.status === 'DONE').length ?? 0;
  const total = submissions.data?.length ?? 0;
  const successRate = total ? Math.round((done / total) * 1000) / 10 : 0;
  const loading = exams.isLoading || students.isLoading || submissions.isLoading;
  const hasError = exams.isError || students.isError || submissions.isError;

  const recent = submissions.data ?? [];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-slate-800">
          Tổng quan hệ thống
        </h1>
        <p className="text-sm text-slate-500">Xem thống kê tổng hợp các kỳ thi, sinh viên và kết quả chấm thi trắc nghiệm.</p>
      </div>

      {hasError && (
        <Alert
          type="warning"
          showIcon
          className="rounded-lg border-amber-200 bg-amber-50"
          message={<span className="font-bold text-amber-800">Lỗi kết nối máy chủ</span>}
          description={<span className="text-amber-700">Không thể kết nối đến máy chủ hoặc phiên làm việc đã hết hạn. Vui lòng đăng nhập lại hoặc kiểm tra dịch vụ backend.</span>}
        />
      )}

      <Row gutter={[24, 24]}>
        {[
          { title: 'Tổng số kỳ thi', value: exams.data?.length ?? 0, icon: <ClipboardList size={24} />, color: 'text-blue-600', bg: 'bg-blue-50' },
          { title: 'Tổng số sinh viên', value: students.data?.length ?? 0, icon: <GraduationCap size={24} />, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { title: 'Bài thi đã nhận', value: total, icon: <UploadCloud size={24} />, color: 'text-cyan-600', bg: 'bg-cyan-50' },
          { title: 'Tỷ lệ thành công', value: successRate, suffix: '%', icon: <CheckCircle2 size={24} />, color: 'text-teal-600', bg: 'bg-teal-50' },
        ].map((item) => (
          <Col xs={24} sm={12} xl={6} key={item.title}>
            <div className="h-full p-5 bg-slate-50/60 border border-slate-100/30 rounded-lg transition-all duration-200 hover:bg-slate-50 hover:-translate-y-0.5">
              {loading ? (
                <Skeleton active paragraph={{ rows: 1 }} className="mt-2" />
              ) : (
                <div className="flex justify-between items-start">
                  <div className="flex flex-col gap-1">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{item.title}</p>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-2xl font-bold text-slate-800">{item.value}</span>
                      {item.suffix && <span className="text-base font-semibold text-slate-400">{item.suffix}</span>}
                    </div>
                  </div>
                  <div className={`p-3 rounded-lg ${item.bg} ${item.color}`}>
                    {item.icon}
                  </div>
                </div>
              )}
            </div>
          </Col>
        ))}
      </Row>

      <div className="space-y-4 pt-4">
        <h3 className="text-base font-bold text-slate-800">Bài làm nộp gần đây</h3>
        <Table
          size="middle"
          rowKey="id"
          loading={submissions.isLoading}
          dataSource={recent}
          pagination={{ pageSize: 5 }} 
          className="border border-slate-100/50 rounded-lg overflow-hidden"
          columns={[
            { title: 'Mã bài thi', dataIndex: 'id', render: (id: string) => <span className="inline-block font-mono font-medium text-xs text-slate-500 bg-slate-50 px-2 py-1 rounded border border-slate-200">{id.slice(0, 8)}</span> },
            { title: 'Loại bài thi', dataIndex: 'examCode', render: (code: string) => <Tag color="blue" className="rounded font-semibold px-2 py-0.5">{getExamTypeLabel(code)}</Tag> },
            { 
              title: 'Điểm số', 
              dataIndex: 'score', 
              render: (value?: number) => value != null ? (
                <span className={`font-bold ${value >= 8 ? 'text-emerald-600' : value >= 5 ? 'text-amber-600' : 'text-rose-600'}`}>
                  {value} / 10
                </span>
              ) : <span className="text-slate-400 font-medium">-</span> 
            },
            { 
              title: 'Trạng thái', 
              dataIndex: 'status', 
              render: (status: string) => (
                <Tag color={status === 'DONE' ? 'success' : status === 'FAILED' ? 'error' : 'warning'} className="font-semibold rounded">
                  {status === 'DONE' ? 'Hoàn thành' : status === 'FAILED' ? 'Lỗi' : 'Đang xử lý'}
                </Tag>
              )
            },
            { title: 'Thời gian nộp', dataIndex: 'submittedAt', render: (value?: string) => <span className="text-sm text-slate-500">{value ? new Date(value).toLocaleString() : '-'}</span> },
          ]}
        />
      </div>
    </div>
  );
};

export default Dashboard;
