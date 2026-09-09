import React, { useState } from 'react';
import { Button, Card, Input, Space, Table, Tag } from 'antd';
import { DownloadOutlined, SearchOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { resources } from '../../api/resources';
import * as XLSX from 'xlsx';

const Results: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const results = useQuery({ queryKey: ['results'], queryFn: resources.results.list });
  const exams = useQuery({ queryKey: ['exams'], queryFn: resources.exams.list });
  const students = useQuery({ queryKey: ['students'], queryFn: resources.students.list });



  const getStudentName = (id: string) => {
    const student = students.data?.find((s) => s.id === id);
    return student ? student.fullName || student.studentCode : id.slice(0, 8);
  };

  const getExamTitle = (id: string) => {
    const exam = exams.data?.find((e) => e.id === id);
    return exam ? exam.title : id.slice(0, 8);
  };

  const filteredData = useMemo(() => {
    const data = results.data ?? [];
    if (!searchText) return data;
    const lowerSearch = searchText.toLowerCase();
    return data.filter((item) => {
      const sName = getStudentName(item.studentId).toLowerCase();
      const eTitle = getExamTitle(item.examId).toLowerCase();
      return sName.includes(lowerSearch) || eTitle.includes(lowerSearch);
    });
  }, [results.data, exams.data, students.data, searchText]);

  const handleExportExcel = () => {
    const dataToExport = filteredData.map((item, index) => {
      const student = students.data?.find((s) => s.id === item.studentId);
      const exam = exams.data?.find((e) => e.id === item.examId);

      const studentName = student ? student.fullName || `${student.firstName || ''} ${student.lastName || ''}`.trim() : '';

      return {
        'STT': index + 1,
        'Mã sinh viên': student?.studentCode || '',
        'Họ và tên': studentName || item.studentId.slice(0, 8),
        'Lớp': student?.className || '',
        'Kỳ thi': exam?.title || item.examId.slice(0, 8),
        'Điểm thi chính thức': item.finalScore ?? '',
        'Thời gian công bố': item.publishedAt ? new Date(item.publishedAt).toLocaleString('vi-VN') : '',
      };
    });

    const worksheet = XLSX.utils.json_to_sheet(dataToExport);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Kết quả");

    worksheet['!cols'] = [
      { wch: 5 },
      { wch: 15 },
      { wch: 25 },
      { wch: 10 },
      { wch: 30 },
      { wch: 20 },
      { wch: 25 },
    ];

    XLSX.writeFile(workbook, "ket_qua_cham_thi.xlsx");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">Kết quả chấm thi</h1>
          <p className="mt-1 text-sm text-slate-500">Tra cứu, đối chiếu và xuất danh sách điểm thi cuối cùng của sinh viên các kỳ thi.</p>
        </div>
        <Button
          type="primary"
          className="rounded font-semibold shadow-sm h-10"
          icon={<DownloadOutlined />}
          onClick={handleExportExcel}
        >
          Xuất điểm Excel
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={results.isLoading || exams.isLoading || students.isLoading}
        dataSource={filteredData}
        className="border border-slate-100/50 rounded-lg overflow-hidden"
        columns={[
          { title: 'Sinh viên', dataIndex: 'studentId', render: (value: string) => <span className="font-bold text-slate-700">{getStudentName(value)}</span> },
          { title: 'Kỳ thi', dataIndex: 'examId', render: (value: string) => <span className="font-semibold text-slate-600">{getExamTitle(value)}</span> },
          {
            title: 'Điểm thi chính thức',
            dataIndex: 'finalScore',
            render: (value?: number) => value != null ? (
              <div className="flex items-center gap-2">
                <span className={`font-bold text-base ${value >= 8 ? 'text-emerald-600' : value >= 5 ? 'text-blue-600' : 'text-red-500'}`}>
                  {value}
                </span>
                <span className="text-xs text-slate-400 font-medium">/ 10</span>
              </div>
            ) : '-'
          },
          { title: 'Thời gian công bố', dataIndex: 'publishedAt', render: (value?: string) => <span className="text-sm text-slate-500">{value ? new Date(value).toLocaleString() : '-'}</span> },
          { title: 'Trạng thái', render: () => <Tag color="success" className="font-bold rounded px-2.5">Đã công bố</Tag> },
        ]}
        title={() => (
          <Space className="w-full justify-between flex-wrap gap-2">
            <span className="text-sm font-semibold text-slate-500">Danh sách điểm thi chính thức</span>
            <Input
              prefix={<SearchOutlined />}
              placeholder="Tìm kiếm kết quả..."
              className="max-w-xs"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Space>
        )}
      />
    </div>
  );
};

// Add useMemo import to avoid compilation error
import { useMemo } from 'react';

export default Results;
