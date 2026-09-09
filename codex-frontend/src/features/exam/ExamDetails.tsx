import React, { useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Card, Table, Tag, Modal, Upload, message, Alert, Spin } from 'antd';
import { ArrowLeft, Upload as UploadIcon, FileSearch, CheckCircle, XCircle } from 'lucide-react';
import { resources, getExamTypeLabel } from '../../api/resources';
import type { Submission } from '../../api/resources';

const { Dragger } = Upload;

import { HolderOutlined } from '@ant-design/icons';

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
      className="flex items-center justify-between p-3 mt-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:border-blue-400 hover:shadow-md transition-all cursor-move group"
    >
       <div className="flex items-center gap-3 overflow-hidden">
          <HolderOutlined className="text-slate-300 group-hover:text-slate-500 cursor-move" />
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-bold text-xs shrink-0">
             {index + 1}
          </span>
          {preview ? (
            <img src={preview} alt="preview" className="w-12 h-12 object-cover rounded shadow-sm border border-slate-200 shrink-0" />
          ) : (
            <div className="w-12 h-12 bg-slate-100 rounded border flex items-center justify-center text-xs text-slate-400 shrink-0">IMG</div>
          )}
          <span className="truncate font-medium text-slate-700 ml-1">{file.name}</span>
       </div>
       <div className="flex gap-2">
         <Button size="small" onClick={() => moveFileStep(index, 'up')} disabled={index === 0 || isUploadingUI}>↑</Button>
         <Button size="small" onClick={() => moveFileStep(index, 'down')} disabled={index === totalLength - 1 || isUploadingUI}>↓</Button>
         <Button size="small" danger onClick={removeFile} disabled={isUploadingUI}>X</Button>
       </div>
    </div>
  );
};

const GradingModal: React.FC<{
  examId: string;
  studentId: string | null;
  exam: any;
  onClose: () => void;
}> = ({ examId, studentId, exam, onClose }) => {
  const queryClient = useQueryClient();
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [isReuploading, setIsReuploading] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);

  const dragItem = React.useRef<number | null>(null);
  const dragOverItem = React.useRef<number | null>(null);

  const { data: submissions } = useQuery({
    queryKey: ['submissions'],
    queryFn: resources.submissions.list,
  });

  const [isUploadingUI, setIsUploadingUI] = useState(false);

  React.useEffect(() => {
    if (!studentId) {
      setIsReuploading(false);
      setSubmission(null);
      setFileList([]);
    } else if (submissions && !isReuploading) {
      const existing = submissions.filter(s => s.examId === examId && s.studentId === studentId).pop();
      setSubmission(existing || null);
    }
  }, [studentId, submissions, examId, isReuploading]);

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

  const uploadProps: any = {
    onRemove: (file: any) => {
      setFileList((prev) => prev.filter((item) => item.uid !== file.uid));
    },
    beforeUpload: (file: any) => {
      setFileList((prev) => [...prev, file]);
      return false;
    },
    fileList,
    multiple: true,
    accept: "image/*",
    disabled: isUploadingUI,
    itemRender: (originNode: any, file: any, currentFileList: any[], actions: any) => {
      const index = fileList.indexOf(file);
      if (index === -1) return null;
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

  const handleUploadAndGrade = async () => {
    if (fileList.length === 0) {
      message.warning('Vui lòng chọn ít nhất 1 ảnh để chấm điểm');
      return;
    }
    
    setIsUploadingUI(true);
    const filesToUpload = fileList.map(f => (f.originFileObj || f) as File);
    
    try {
      const data = await resources.submissions.upload({ files: filesToUpload, examId, studentId: studentId! });
      const gradedData = await resources.submissions.grade(data.id);
      
      message.success(`Đã nhận diện và chấm ${filesToUpload.length} trang thành công`);
      setSubmission(gradedData);
      setFileList([]);
      setIsReuploading(false);
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      queryClient.invalidateQueries({ queryKey: ['results'] });
    } catch (err) {
      message.error(`Chấm điểm thất bại cho ${filesToUpload.length} ảnh`);
    } finally {
      setIsUploadingUI(false);
    }
  };

  const handleRegrade = async () => {
    if (!submission) return;
    setIsUploadingUI(true);
    try {
      const gradedData = await resources.submissions.grade(submission.id);
      message.success('Đã cập nhật lại điểm số theo đáp án mới!');
      setSubmission(gradedData);
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      queryClient.invalidateQueries({ queryKey: ['results'] });
    } catch (err) {
      message.error('Lỗi khi cập nhật điểm');
    }
    setIsUploadingUI(false);
  };

  const parseJson = (str?: string) => {
    if (!str) return {};
    try {
      return JSON.parse(str);
    } catch {
      return {};
    }
  };

  const answerKey = parseJson(exam?.answerKey);
  const maxQ = Math.max(0, ...Object.keys(answerKey).map(Number).filter(n => !isNaN(n)), 20);

  const getDetectedAnswers = () => {
    if (!submission?.content) return {};
    const content = parseJson(submission.content);
    if (content.results) return content.results;
    if (content.answers) return content.answers;
    return content;
  };

  const detectedAnswers = getDetectedAnswers();

  return (
    <Modal
      open={!!studentId}
      onCancel={onClose}
      footer={null}
      width={800}
      title={<span className="text-lg font-bold text-slate-800">Thông tin chi tiết chấm điểm</span>}
      destroyOnClose
    >
      {!submission && !isUploadingUI && (
        <div className="py-4">
          <Dragger
            {...uploadProps}
            className="border-2 border-dashed border-blue-200 hover:border-blue-400 bg-blue-50/10 rounded transition-colors duration-300"
          >
            <div className="py-12">
              <div className="mx-auto w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center text-blue-500 mb-4">
                <UploadIcon size={28} />
              </div>
              <p className="text-base font-bold text-slate-700">Nhấp hoặc kéo thả ảnh bài thi để chấm điểm</p>
              <p className="text-sm text-slate-500 mt-2 px-4">Bạn có thể sắp xếp lại thứ tự ảnh trước khi chấm.</p>
            </div>
          </Dragger>
          <Button 
             type="primary" 
             size="large" 
             className="w-full mt-6 bg-blue-600 hover:bg-blue-700 font-bold" 
             loading={isUploadingUI}
             onClick={handleUploadAndGrade}
             disabled={fileList.length === 0}
          >
             Bắt đầu chấm điểm ({fileList.length} ảnh)
          </Button>
        </div>
      )}

      {isUploadingUI && (
        <div className="py-16 flex flex-col items-center justify-center">
          <Spin size="large" />
          <p className="mt-4 text-blue-600 font-medium">Đang tải lên và xử lý các trang bài thi...</p>
        </div>
      )}

      {submission && !isUploadingUI && (
        <div className="py-4 space-y-6">
          <div className="flex items-center justify-between bg-blue-50/30 p-4 rounded border border-blue-100">
            <div>
              <p className="text-sm font-semibold text-slate-500">Điểm số</p>
              <p className="text-2xl font-bold text-blue-600">{submission.score} / 10</p>
            </div>
            {(() => {
              let timeStr = '-';
              try {
                if (submission.content) {
                  const parsed = JSON.parse(submission.content);
                  if (parsed.executionTime != null) {
                    timeStr = parsed.executionTime >= 1000 ? `${(parsed.executionTime / 1000).toFixed(2)}s` : `${parsed.executionTime}ms`;
                  }
                }
              } catch (e) {}
              return (
                <div>
                  <p className="text-sm font-semibold text-slate-500 text-center">Thời gian chấm</p>
                  <p className="mt-1 font-bold text-slate-700 text-center bg-slate-100 px-2 rounded">{timeStr}</p>
                </div>
              );
            })()}
            <div>
              <p className="text-sm font-semibold text-slate-500 text-right">Trạng thái</p>
              <Tag color={submission.status === 'DONE' ? 'success' : 'error'} className="mt-1 font-bold">
                {submission.status === 'DONE' ? 'Hoàn thành' : 'Thất bại'}
              </Tag>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <FileSearch size={18} className="text-blue-500" />
              Bảng so sánh đáp án chi tiết
            </h3>
            
            {!Object.keys(answerKey).length && (
              <Alert type="warning" showIcon message="Chưa cấu hình đáp án chuẩn cho kỳ thi này. Không thể hiển thị bảng đối chiếu." className="rounded" />
            )}

            {Object.keys(answerKey).length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
                {Array.from({ length: maxQ }).map((_, idx) => {
                  const qNum = (idx + 1).toString();
                  const correct = answerKey[qNum] || '-';
                  const studentAns = detectedAnswers[qNum] || '-';
                  const isMatch = correct !== '-' && correct.toLowerCase() === studentAns.toLowerCase();

                  return (
                    <div key={qNum} className={`flex items-center justify-between p-2 rounded border ${isMatch ? 'bg-emerald-50/20 border-emerald-100' : 'bg-red-50/20 border-red-100'}`}>
                      <span className="font-bold text-slate-500 w-5 text-xs">{qNum}.</span>
                      <div className="flex gap-1.5 text-xs font-semibold items-center">
                        <span className="text-slate-400">Đáp án: <span className="text-slate-700">{correct}</span></span>
                        <span className="text-slate-300">|</span>
                        <span className={isMatch ? 'text-emerald-600 font-bold' : 'text-red-600 font-bold'}>{studentAns}</span>
                      </div>
                      {isMatch ? <CheckCircle size={14} className="text-emerald-500" /> : <XCircle size={14} className="text-red-400" />}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
          
          <div className="flex justify-end pt-2">
             <Button onClick={handleRegrade} className="rounded font-medium mr-2" type="default" loading={isUploadingUI}>Chấm lại</Button>
             <Button onClick={() => { setSubmission(null); setIsReuploading(true); }} className="rounded font-medium mr-2">Tải ảnh khác</Button>
             <Button type="primary" onClick={onClose} className="rounded font-bold bg-blue-600">Hoàn tất</Button>
          </div>
        </div>
      )}
    </Modal>
  );
};

const ExamDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);

  const exams = useQuery({ queryKey: ['exams'], queryFn: resources.exams.list });
  const students = useQuery({ queryKey: ['students'], queryFn: resources.students.list });
  const results = useQuery({ queryKey: ['results'], queryFn: resources.results.list });
  const submissions = useQuery({ queryKey: ['submissions'], queryFn: resources.submissions.list });

  const exam = useMemo(() => exams.data?.find(e => e.id === id), [exams.data, id]);

  const getStudentStatus = (studentId: string) => {
    const studentSubs = submissions.data?.filter(s => s.examId === id && s.studentId === studentId);
    if (!studentSubs?.length) return { status: 'PENDING', score: '-' };
    
    const result = results.data?.find(r => r.examId === id && r.studentId === studentId);
    if (result) return { status: 'DONE', score: result.finalScore };

    const latest = studentSubs[studentSubs.length - 1];
    return { status: latest.status, score: latest.score ?? '-' };
  };

  if (exams.isLoading) return <div className="p-8"><Spin /></div>;
  if (!exam) return <Alert type="error" message="Không tìm thấy kỳ thi phù hợp!" />;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center gap-4">
        <Button 
          icon={<ArrowLeft size={16} />} 
          type="text" 
          onClick={() => navigate('/exams')}
          className="hover:bg-slate-100 rounded"
        />
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{exam.title}</h1>
          <p className="text-xs font-semibold text-slate-500">{exam.subject || 'Không rõ môn học'} • {getExamTypeLabel(exam.examType)}</p>
        </div>
      </div>

      <Table
        rowKey="id"
        loading={students.isLoading || submissions.isLoading || results.isLoading}
        dataSource={students.data ?? []}
        pagination={{ pageSize: 10 }}
        className="border border-slate-100/50 rounded-lg overflow-hidden"
        columns={[
          { title: 'Mã sinh viên', dataIndex: 'studentCode', render: (val) => <span className="font-semibold text-slate-500">{val || '-'}</span> },
          { title: 'Họ và tên', dataIndex: 'fullName', render: (val, record) => <span className="font-bold text-slate-800">{val || `${record.firstName || ''} ${record.lastName || ''}`}</span> },
          { title: 'Lớp', dataIndex: 'className', render: (val) => <span className="font-semibold text-slate-600">{val || '-'}</span> },
          { 
            title: 'Trạng thái', 
            key: 'status',
            render: (_, record) => {
              const { status } = getStudentStatus(record.id);
              if (status === 'DONE') return <Tag color="success" className="font-bold px-3">Đã chấm</Tag>;
              if (status === 'FAILED') return <Tag color="error" className="font-bold px-3">Lỗi</Tag>;
              return <Tag color="default" className="font-bold px-3">Chưa chấm</Tag>;
            }
          },
          { 
            title: 'Điểm số', 
            key: 'score',
            render: (_, record) => {
              const { score } = getStudentStatus(record.id);
              return <span className={`font-bold text-base ${score !== '-' ? 'text-blue-600' : 'text-slate-300'}`}>{score}</span>;
            }
          },
          {
            title: 'Hành động',
            key: 'action',
            render: (_, record) => {
              const { status } = getStudentStatus(record.id);
              const isGraded = status === 'DONE' || status === 'FAILED';
              return (
                <Button 
                  type={isGraded ? 'default' : 'primary'}
                  className="font-semibold shadow-sm rounded"
                  onClick={() => setSelectedStudent(record.id)}
                >
                  {isGraded ? 'Xem chi tiết' : 'Chấm điểm'}
                </Button>
              );
            }
          }
        ]}
      />

      <GradingModal 
        examId={id!} 
        studentId={selectedStudent} 
        exam={exam} 
        onClose={() => setSelectedStudent(null)} 
      />
    </div>
  );
};

export default ExamDetails;
