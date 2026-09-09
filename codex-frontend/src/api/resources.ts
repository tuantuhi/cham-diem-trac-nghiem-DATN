import api from './axios';

type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};

export type Exam = {
  id: string;
  title: string;
  subject?: string;
  description?: string;
  examType: string;
  answerKey?: string;
  startTime?: string;
  endTime?: string;
};

export type Student = {
  id: string;
  studentCode?: string;
  firstName?: string;
  lastName?: string;
  fullName?: string;
  className?: string;
  email?: string;
};

export type Submission = {
  id: string;
  examId: string;
  studentId: string;
  examCode?: string;
  imageUrl?: string;
  status: 'PENDING' | 'PROCESSING' | 'DONE' | 'FAILED' | string;
  score?: number;
  content?: string;
  submittedAt?: string;
};

export type Result = {
  id: string;
  studentId: string;
  examId: string;
  gradeId?: string;
  finalScore: number;
  publishedAt?: string;
};

const unwrap = <T>(response: { data: ApiResponse<T> }) => response.data.data;

export const getExamTypeLabel = (type?: string) => {
  switch (type) {
    case 'YOLO': return 'Phiếu khoanh';
    case 'OMR_20': return 'Phiếu tô 20 đáp án';
    case 'OMR_50': return 'Phiếu tô 50 đáp án';
    default: return type || '-';
  }
};

export const resources = {
  exams: {
    list: async () => unwrap<Exam[]>(await api.get('/exams')),
    create: async (payload: Partial<Exam>) => unwrap<Exam>(await api.post('/exams', payload)),
    update: async (id: string, payload: Partial<Exam>) => unwrap<Exam>(await api.put(`/exams/${id}`, payload)),
    remove: async (id: string) => unwrap<void>(await api.delete(`/exams/${id}`)),
    saveAnswerKey: async (id: string, answerKey: Record<string, string>) =>
      unwrap<Exam>(await api.post(`/exams/${id}/answer-keys`, answerKey)),
  },
  students: {
    list: async () => unwrap<Student[]>(await api.get('/students')),
    create: async (payload: Partial<Student>) => unwrap<Student>(await api.post('/students', payload)),
    import: async (payload: Partial<Student>[]) => unwrap<Student[]>(await api.post('/students/import', payload)),
    remove: async (id: string) => unwrap<void>(await api.delete(`/students/${id}`)),
  },
  submissions: {
    list: async () => unwrap<Submission[]>(await api.get('/submissions')),
    upload: async (payload: { files: File[]; examId: string; studentId: string }) => {
      const formData = new FormData();
      payload.files.forEach(file => formData.append('files', file));
      formData.append('examId', payload.examId);
      formData.append('studentId', payload.studentId);
      return unwrap<Submission>(
        await api.post('/submissions/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        }),
      );
    },
    grade: async (submissionId: string) =>
      unwrap<Submission>(await api.post('/submissions/grade', null, { params: { submissionId } })),
  },
  results: {
    list: async () => unwrap<Result[]>(await api.get('/results')),
    exportFile: async () => api.get('/results/export/excel', { responseType: 'blob' }),
  },
};
