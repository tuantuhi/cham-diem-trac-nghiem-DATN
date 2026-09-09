package com.codex.backend.student.application.port.in;
import com.codex.backend.student.application.dto.StudentRequest;
import com.codex.backend.student.application.dto.StudentResponse;
import java.util.List;
import java.util.UUID;
public interface StudentUseCase {
    StudentResponse create(StudentRequest request);
    StudentResponse getById(UUID id);
    List<StudentResponse> list();
    List<StudentResponse> importStudents(List<StudentRequest> requests);
    void delete(UUID id);
}
