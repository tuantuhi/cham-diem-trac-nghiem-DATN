import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, Drawer, Form, Input, Modal, Space, Table, Tag, message, InputNumber, Radio, Select } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, KeyRound } from 'lucide-react';
import { resources, getExamTypeLabel } from '../../api/resources';
import type { Exam } from '../../api/resources';

const AnswerKeyBuilder: React.FC<{
  exam: Exam;
  onClose: () => void;
  onSave: (payload: Record<string, string>) => void;
  loading: boolean;
}> = ({ exam, onClose, onSave, loading }) => {
  const [numQuestions, setNumQuestions] = useState<number>(50);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  useEffect(() => {
    if (exam.examType === 'OMR_20') setNumQuestions(20);
    else if (exam.examType === 'OMR_50') setNumQuestions(50);

    if (exam.answerKey) {
      try {
        const parsed = JSON.parse(exam.answerKey);
        setAnswers(parsed);
        const maxQ = Math.max(0, ...Object.keys(parsed).map(Number).filter(n => !isNaN(n)));
        if (maxQ > 0) setNumQuestions(maxQ);
      } catch {
        // invalid json
      }
    }
  }, [exam]);

  const handleAnswerChange = (q: number, ans: string) => {
    setAnswers(prev => ({ ...prev, [q.toString()]: ans }));
  };

  const handleSave = () => {
    const cleanAnswers: Record<string, string> = {};
    for (let i = 1; i <= numQuestions; i++) {
      if (answers[i]) {
        cleanAnswers[i] = answers[i];
      }
    }
    onSave(cleanAnswers);
  };

  return (
    <Modal
      title={<span className="text-lg font-bold text-slate-800">Đáp án chuẩn: {exam.title}</span>}
      open={true}
      onCancel={onClose}
      onOk={handleSave}
      okButtonProps={{ loading }}
      cancelButtonProps={{ className: 'font-medium' }}
      width={750}
    >
      <div className="mb-6 bg-slate-50 p-4 rounded flex items-center gap-4 border border-slate-200">
        <span className="font-bold text-slate-700">Tổng số câu hỏi:</span>
        <InputNumber
          min={1}
          max={200}
          value={numQuestions}
          onChange={(val) => setNumQuestions(val || 50)}
          className="rounded w-24 font-bold"
          size="middle"
        />
        <span className="text-sm font-semibold text-blue-600 ml-auto bg-blue-50 px-3 py-1.5 rounded border border-blue-100">
          Đã điền: {Object.keys(answers).length} / {numQuestions} câu
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[55vh] overflow-y-auto pr-3 custom-scrollbar py-2">
        {Array.from({ length: numQuestions }).map((_, idx) => {
          const qNum = idx + 1;
          const isAnswered = !!answers[qNum];
          return (
            <div 
              key={qNum} 
              className={`flex items-center justify-between p-2 rounded border transition-colors ${isAnswered ? 'bg-blue-50/50 border-blue-200' : 'bg-white border-slate-200 hover:border-blue-300'}`}
            >
              <span className={`font-bold w-8 text-center ${isAnswered ? 'text-blue-600' : 'text-slate-400'}`}>{qNum}.</span>
              <Radio.Group 
                value={answers[qNum]} 
                onChange={(e) => handleAnswerChange(qNum, e.target.value)}
                size="middle"
                buttonStyle="solid"
                className="flex shadow-sm rounded overflow-hidden"
              >
                {['A', 'B', 'C', 'D'].map(opt => (
                  <Radio.Button 
                    key={opt} 
                    value={opt} 
                    className={`w-9 text-center px-0 font-bold transition-colors ${answers[qNum] === opt ? '!bg-blue-600 !border-blue-600 !text-white' : ''}`}
                  >
                    {opt}
                  </Radio.Button>
                ))}
              </Radio.Group>
            </div>
          );
        })}
      </div>
    </Modal>
  );
};

const Exams: React.FC = () => {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [answerKeyExam, setAnswerKeyExam] = useState<Exam | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const exams = useQuery({ queryKey: ['exams'], queryFn: resources.exams.list });

  const createExam = useMutation({
    mutationFn: resources.exams.create,
    onSuccess: () => {
      message.success('Đã lưu kỳ thi thành công!');
      form.resetFields();
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ['exams'] });
    },
  });

  const removeExam = useMutation({
    mutationFn: resources.exams.remove,
    onSuccess: () => {
      message.success('Kỳ thi đã được xóa thành công!');
      queryClient.invalidateQueries({ queryKey: ['exams'] });
    },
  });

  const saveAnswerKey = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, string> }) => resources.exams.saveAnswerKey(id, payload),
    onSuccess: () => {
      message.success('Cập nhật đáp án chuẩn thành công!');
      setAnswerKeyExam(null);
      queryClient.invalidateQueries({ queryKey: ['exams'] });
    },
  });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">
            Quản lý kỳ thi
          </h1>
          <p className="text-sm text-slate-500">Tạo kỳ thi mới để quản lý thông tin và cấu hình đáp án chuẩn chấm trắc nghiệm.</p>
        </div>
        <Button 
          type="primary" 
          icon={<Plus size={16} />} 
          className="h-10 px-5 font-semibold shadow-sm"
          onClick={() => setOpen(true)}
        >
          Kỳ thi mới
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={exams.isLoading}
        dataSource={exams.data ?? []}
        pagination={{ pageSize: 8 }}
        className="border border-slate-100/50 rounded-lg overflow-hidden"
        columns={[
          { title: 'Tên kỳ thi', dataIndex: 'title', render: (value: string) => <span className="font-bold text-slate-800 text-sm">{value}</span> },
          { title: 'Môn học', dataIndex: 'subject', render: (value: string) => <span className="font-semibold text-slate-500">{value || '-'}</span> },
          { title: 'Loại bài thi', dataIndex: 'examType', render: (value: string) => <Tag color="blue" className="rounded font-bold px-3.5 py-0.5">{getExamTypeLabel(value)}</Tag> },
          { title: 'Đáp án chuẩn', dataIndex: 'answerKey', render: (value?: string) => value ? <Tag color="success" className="rounded font-bold px-3.5 py-0.5">Đã cấu hình</Tag> : <Tag color="error" className="rounded font-bold px-3.5 py-0.5">Chưa cấu hình</Tag> },
          {
            title: 'Hành động',
            render: (_, record: Exam) => (
              <Space size="middle">
                <Button 
                  size="middle" 
                  type="primary"
                  className="font-semibold shadow-sm" 
                  onClick={() => navigate(`/exams/${record.id}`)}
                >
                  Xem chi tiết
                </Button>
                <Button 
                  size="middle" 
                  icon={<KeyRound size={14} />}
                  className="font-semibold text-blue-600 shadow-sm" 
                  onClick={() => setAnswerKeyExam(record)}
                >
                  Đáp án
                </Button>
                <Button 
                  size="middle" 
                  danger 
                  icon={<Trash2 size={14} />} 
                  className="rounded shadow-sm hover:shadow-md transition-all bg-white" 
                  onClick={() => {
                    Modal.confirm({
                      title: 'Xóa kỳ thi này?',
                      content: 'Hành động này không thể hoàn tác. Tất cả các bài nộp và kết quả chấm liên quan sẽ bị xóa.',
                      okText: 'Xác nhận xóa',
                      okType: 'danger',
                      cancelText: 'Hủy bỏ',
                      onOk: () => removeExam.mutate(record.id)
                    });
                  }} 
                />
              </Space>
            ),
          },
        ]}
      />

      <Drawer 
        title={<span className="font-bold text-lg text-slate-800">Thêm kỳ thi mới</span>} 
        open={open} 
        onClose={() => setOpen(false)} 
        width={450}
      >
        <Form layout="vertical" form={form} onFinish={(values) => createExam.mutate(values)} initialValues={{ examType: 'OMR_50' }} className="mt-2">
          <Form.Item name="title" label={<span className="font-bold text-slate-700">Tên kỳ thi</span>} rules={[{ required: true, message: 'Vui lòng nhập tên kỳ thi!' }]}>
            <Input size="large" className="rounded font-medium" placeholder="Ví dụ: Thi giữa kỳ Vật lý" />
          </Form.Item>
          <Form.Item name="subject" label={<span className="font-bold text-slate-700">Môn học</span>}>
            <Input size="large" className="rounded font-medium" placeholder="Ví dụ: Vật lý" />
          </Form.Item>
          <Form.Item name="description" label={<span className="font-bold text-slate-700">Mô tả</span>}>
            <Input.TextArea rows={4} className="rounded font-medium resize-none" placeholder="Chi tiết mô tả kỳ thi (tùy chọn)..." />
          </Form.Item>
          <Form.Item name="examType" label={<span className="font-bold text-slate-700">Loại phiếu trả lời</span>}>
            <Select
              size="large"
              className="rounded font-medium"
              options={[
                { label: 'Phiếu tô 50 đáp án', value: 'OMR_50' },
                { label: 'Phiếu tô 20 đáp án', value: 'OMR_20' },
                { label: 'Phiếu khoanh', value: 'YOLO' },
              ]}
            />
          </Form.Item>
          <div className="pt-4">
            <Button type="primary" htmlType="submit" loading={createExam.isPending} className="w-full h-10 font-semibold shadow-sm">
              Lưu kỳ thi
            </Button>
          </div>
        </Form>
      </Drawer>

      {answerKeyExam && (
        <AnswerKeyBuilder 
          exam={answerKeyExam}
          onClose={() => setAnswerKeyExam(null)}
          onSave={(payload) => saveAnswerKey.mutate({ id: answerKeyExam.id, payload })}
          loading={saveAnswerKey.isPending}
        />
      )}
    </div>
  );
};

export default Exams;
