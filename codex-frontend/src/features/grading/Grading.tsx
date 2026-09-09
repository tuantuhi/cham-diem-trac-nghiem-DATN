import React, { useMemo, useState, useRef } from 'react';
import { Alert, Button, Card, Form, Select, Table, Tag, Upload, message, Space } from 'antd';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { InboxOutlined, ArrowUpOutlined, ArrowDownOutlined, DeleteOutlined, PlayCircleOutlined, HolderOutlined } from '@ant-design/icons';
import { resources, getExamTypeLabel } from '../../api/resources';

const { Dragger } = Upload;

const SortableUploadListItem: React.FC<{
  file: any;
  index: number;
  totalLength: number;
  moveFileStep: (index: number, direction: 'up' | 'down') => void;
  removeFile: () => void;
  isUploadingUI: boolean;
  onDragStart: (e: React.DragEvent, index: number) => void;
  onDragEnter: (e: React.DragEvent, index: number) => void;
  onDragEnd: (e: React.DragEvent) => void;
}> = ({ file, index, totalLength, moveFileStep, removeFile, isUploadingUI, onDragStart, onDragEnter, onDragEnd }) => {
  const [preview, setPreview] = useState<string>('');

  React.useEffect(() => {
    const f = file.originFileObj || file;
    if (f && f.type?.startsWith('image/')) {
      const url = URL.createObjectURL(f);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  return (
    <div 
      draggable={!isUploadingUI}
      onDragStart={(e) => onDragStart(e, index)}
      onDragEnter={(e) => onDragEnter(e, index)}
      onDragEnd={onDragEnd}
      onDragOver={(e) => e.preventDefault()}
      className="flex items-center justify-between p-3 mt-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:border-indigo-400 hover:shadow-md transition-all cursor-move group"
    >
       <div className="flex items-center gap-3 overflow-hidden">
          <HolderOutlined className="text-slate-300 group-hover:text-slate-500 cursor-move" />
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 font-bold text-xs shrink-0">
             {index + 1}
          </span>
          {preview ? (
            <img src={preview} alt="preview" className="w-12 h-12 object-cover rounded shadow-sm border border-slate-200 shrink-0" />
          ) : (
            <div className="w-12 h-12 bg-slate-100 rounded border flex items-center justify-center text-xs text-slate-400 shrink-0">IMG</div>
          )}
          <span className="truncate font-medium text-slate-700 ml-1">{file.name}</span>
       </div>
       <Space>
         <Button size="small" icon={<ArrowUpOutlined />} onClick={() => moveFileStep(index, 'up')} disabled={index === 0 || isUploadingUI} />
         <Button size="small" icon={<ArrowDownOutlined />} onClick={() => moveFileStep(index, 'down')} disabled={index === totalLength - 1 || isUploadingUI} />
         <Button size="small" danger icon={<DeleteOutlined />} onClick={removeFile} disabled={isUploadingUI} />
       </Space>
    </div>
  );
};

const Grading: React.FC = () => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const exams = useQuery({ queryKey: ['exams'], queryFn: resources.exams.list });
  const students = useQuery({ queryKey: ['students'], queryFn: resources.students.list });
  const submissions = useQuery({ queryKey: ['submissions'], queryFn: resources.submissions.list });

  const [isUploadingUI, setIsUploadingUI] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  const dragItem = useRef<number | null>(null);
  const dragOverItem = useRef<number | null>(null);

  const examOptions = useMemo(
    () => (exams.data ?? []).map((exam) => ({ label: `${exam.title} (${getExamTypeLabel(exam.examType)})`, value: exam.id })),
    [exams.data],
  );
  const studentOptions = useMemo(
    () => (students.data ?? []).map((student) => ({ label: `${student.fullName || student.studentCode} ${student.className ? `- ${student.className}` : ''}`, value: student.id })),
    [students.data],
  );

  const moveFileStep = (index: number, direction: 'up' | 'down') => {
    const newFileList = [...fileList];
    if (direction === 'up' && index > 0) {
      [newFileList[index - 1], newFileList[index]] = [newFileList[index], newFileList[index - 1]];
    } else if (direction === 'down' && index < newFileList.length - 1) {
      [newFileList[index + 1], newFileList[index]] = [newFileList[index], newFileList[index + 1]];
    }
    setFileList(newFileList);
  };

  const handleDragStart = (e: React.DragEvent, position: number) => {
    dragItem.current = position;
    setTimeout(() => {
      if (e.target instanceof HTMLElement) e.target.style.opacity = '0.4';
    }, 0);
  };

  const handleDragEnter = (e: React.DragEvent, position: number) => {
    dragOverItem.current = position;
  };

  const handleDragEnd = (e: React.DragEvent) => {
    if (e.target instanceof HTMLElement) e.target.style.opacity = '1';
    
    if (dragItem.current !== null && dragOverItem.current !== null && dragItem.current !== dragOverItem.current) {
      const newFileList = [...fileList];
      const draggedItemContent = newFileList[dragItem.current];
      newFileList.splice(dragItem.current, 1);
      newFileList.splice(dragOverItem.current, 0, draggedItemContent);
      setFileList(newFileList);
    }
    dragItem.current = null;
    dragOverItem.current = null;
  };

  const uploadProps: UploadProps = {
    onRemove: (file) => {
      setFileList((prev) => prev.filter((item) => item.uid !== file.uid));
    },
    beforeUpload: (file) => {
      setFileList((prev) => [...prev, file]);
      return false; // Prevent auto upload
    },
    fileList,
    multiple: true,
    accept: "image/*",
    disabled: isUploadingUI,
    itemRender: (originNode, file, currentFileList, actions) => {
      const index = fileList.indexOf(file);
      if (index === -1) return null; // safety check
      return (
        <SortableUploadListItem 
          key={file.uid || index}
          file={file} 
          index={index} 
          totalLength={fileList.length}
          moveFileStep={moveFileStep} 
          removeFile={() => actions.remove()} 
          isUploadingUI={isUploadingUI} 
          onDragStart={handleDragStart}
          onDragEnter={handleDragEnter}
          onDragEnd={handleDragEnd}
        />
      );
    }
  };

  const handleGrade = async () => {
    if (fileList.length === 0) {
      message.warning('Vui lòng chọn ít nhất 1 ảnh để chấm điểm');
      return;
    }
    
    try {
      const values = await form.validateFields();
      setIsUploadingUI(true);
      
      const filesToUpload = fileList.map(f => (f.originFileObj || f) as File);
      
      const data = await resources.submissions.upload({
        files: filesToUpload,
        examId: values.examId,
        studentId: values.studentId
      });
      
      await resources.submissions.grade(data.id);
      
      message.success(`Đã xử lý và chấm điểm xong ${fileList.length} ảnh!`);
      setFileList([]);
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      queryClient.invalidateQueries({ queryKey: ['results'] });
    } catch (err) {
      message.error('Lỗi khi chấm điểm');
    } finally {
      setIsUploadingUI(false);
    }
  };

  const getStudentName = (id: string) => {
    const student = students.data?.find((s) => s.id === id);
    return student ? student.fullName || student.studentCode : id.slice(0, 8);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Hệ thống chấm điểm</h1>
        <p className="mt-2 text-base text-slate-500 max-w-2xl">Tải lên phiếu trả lời của học sinh và xem AI của chúng tôi ngay lập tức chấm điểm và phân tích kết quả với độ chính xác cao.</p>
      </div>

      {(examOptions.length === 0 || studentOptions.length === 0) && (
        <Alert
          type="warning"
          showIcon
          className="rounded-xl border-amber-200 bg-amber-50"
          message="Yêu cầu thiết lập"
          description="Vui lòng tạo ít nhất một bài kiểm tra và đăng ký một học sinh trước khi tải lên phiếu trả lời."
        />
      )}

      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <Card 
          title={<span className="font-bold text-slate-800">Tải bài thi lên</span>} 
          className="rounded-2xl border-slate-200 shadow-sm hover:shadow-md transition-shadow bg-white/50 backdrop-blur-sm"
        >
          <Form form={form} layout="vertical">
            <Form.Item label={<span className="font-medium text-slate-700">Chọn bài thi</span>} name="examId" rules={[{ required: true }]}>
              <Select size="large" loading={exams.isLoading} options={examOptions} placeholder="Chọn bài thi để chấm điểm" />
            </Form.Item>
            <Form.Item label={<span className="font-medium text-slate-700">Chọn học sinh</span>} name="studentId" rules={[{ required: true }]}>
              <Select size="large" loading={students.isLoading} options={studentOptions} placeholder="Tìm kiếm theo tên hoặc ID học sinh" showSearch optionFilterProp="label" />
            </Form.Item>
            <Dragger
              {...uploadProps}
              className="mt-6 border-2 border-dashed border-indigo-200 hover:border-indigo-400 bg-indigo-50/30 rounded-xl transition-colors duration-300"
            >
              <div className="py-6">
                <p className="ant-upload-drag-icon">
                  <div className="mx-auto w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-500 mb-4 shadow-inner">
                    <InboxOutlined style={{ fontSize: '28px' }} />
                  </div>
                </p>
                <p className="text-base font-semibold text-slate-700">Nhấn hoặc kéo thả ảnh để tải lên</p>
                <p className="text-sm text-slate-500 mt-2 px-4">Bạn có thể tải lên nhiều hình ảnh và kéo-thả để sắp xếp lại trước khi chấm điểm.</p>
              </div>
            </Dragger>

            <Button 
               type="primary" 
               size="large" 
               icon={<PlayCircleOutlined />} 
               className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700" 
               loading={isUploadingUI}
               onClick={handleGrade}
               disabled={fileList.length === 0}
            >
               Bắt đầu chấm điểm ({fileList.length} ảnh)
            </Button>
          </Form>
        </Card>

        <Card
          title={<span className="font-bold text-slate-800">Hàng đợi đang xử lí</span>}
          className="rounded-2xl border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm"
          extra={<Button type="default" className="rounded-lg font-medium" onClick={() => submissions.refetch()}>Làm mới</Button>}
        >
          <Table
            rowKey="id"
            loading={submissions.isLoading || students.isLoading}
            dataSource={submissions.data ?? []}
            pagination={{ pageSize: 8 }}
            columns={[
              { title: 'Student', dataIndex: 'studentId', render: (value: string) => <span className="font-semibold text-slate-700">{getStudentName(value)}</span> },
              { title: 'Loại bài thi', dataIndex: 'examCode', render: (code: string) => <Tag className="rounded-full bg-indigo-50 text-indigo-600 border-indigo-200 font-medium px-3">{getExamTypeLabel(code)}</Tag> },
              { 
                title: 'Score', 
                dataIndex: 'score', 
                render: (value?: number) => value != null ? (
                  <div className="flex items-center gap-2">
                    <span className={`font-bold text-lg ${value >= 8 ? 'text-emerald-600' : value >= 5 ? 'text-amber-500' : 'text-red-500'}`}>
                      {value}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">/ 10</span>
                  </div>
                ) : '-' 
              },
              { 
                title: 'Status', 
                dataIndex: 'status', 
                render: (status: string) => (
                  <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${status === 'DONE' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : status === 'FAILED' ? 'bg-red-50 text-red-600 border-red-200' : 'bg-amber-50 text-amber-600 border-amber-200'}`}>
                    {status}
                  </span>
                )
              },
              { 
                title: 'Thời gian chấm', 
                dataIndex: 'content', 
                render: (content?: string) => {
                  if (!content) return <span className="text-sm text-slate-400">-</span>;
                  try {
                    const parsed = JSON.parse(content);
                    if (parsed.executionTime != null) {
                      const timeStr = parsed.executionTime >= 1000 ? `${(parsed.executionTime / 1000).toFixed(2)}s` : `${parsed.executionTime}ms`;
                      return <span className="text-sm font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded-md">{timeStr}</span>;
                    }
                  } catch (e) {
                    // ignore
                  }
                  return <span className="text-sm text-slate-400">-</span>;
                }
              },
              { title: 'Submitted', dataIndex: 'submittedAt', render: (value?: string) => <span className="text-sm text-slate-500">{value ? new Date(value).toLocaleString() : '-'}</span> },
            ]}
          />
        </Card>
      </div>
    </div>
  );
};

export default Grading;

