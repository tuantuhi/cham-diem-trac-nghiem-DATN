package com.codex.backend.student.application.service;
import com.codex.backend.student.application.dto.StudentRequest;
import com.codex.backend.student.application.dto.StudentResponse;
import com.codex.backend.student.application.port.in.StudentUseCase;
import com.codex.backend.student.application.port.out.StudentRepositoryPort;
import com.codex.backend.student.domain.entity.Student;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class StudentService implements StudentUseCase {
    private final StudentRepositoryPort repositoryPort;
    @Override
    public StudentResponse create(StudentRequest request) {
        return toResponse(repositoryPort.save(toEntity(request)));
    }
    @Override
    public StudentResponse getById(UUID id) {
        return repositoryPort.findById(id).map(this::toResponse).orElseThrow();
    }

    @Override
    public List<StudentResponse> list() {
        return repositoryPort.findAll().stream().map(this::toResponse).toList();
    }

    @Override
    public List<StudentResponse> importStudents(List<StudentRequest> requests) {
        return requests.stream().map(this::create).toList();
    }

    @Override
    public void delete(UUID id) {
        repositoryPort.deleteById(id);
    }

    private Student toEntity(StudentRequest request) {
        LocalDateTime now = LocalDateTime.now();
        String[] names = splitName(request);
        return Student.builder()
                .id(UUID.randomUUID())
                .studentCode(request.getStudentCode())
                .firstName(valueOr(request.getFirstName(), names[0]))
                .lastName(valueOr(request.getLastName(), names[1]))
                .className(request.getClassName())
                .email(request.getEmail())
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    private StudentResponse toResponse(Student student) {
        StudentResponse response = new StudentResponse();
        response.setId(student.getId());
        response.setStudentCode(student.getStudentCode());
        response.setFirstName(student.getFirstName());
        response.setLastName(student.getLastName());
        response.setFullName(((student.getFirstName() == null ? "" : student.getFirstName()) + " " +
                (student.getLastName() == null ? "" : student.getLastName())).trim());
        response.setClassName(student.getClassName());
        response.setEmail(student.getEmail());
        response.setCreatedAt(student.getCreatedAt());
        response.setUpdatedAt(student.getUpdatedAt());
        return response;
    }

    private String[] splitName(StudentRequest request) {
        if (request.getFullName() == null || request.getFullName().isBlank()) {
            return new String[]{"", ""};
        }
        String fullName = request.getFullName().trim();
        int lastSpace = fullName.lastIndexOf(' ');
        if (lastSpace < 0) {
            return new String[]{fullName, ""};
        }
        return new String[]{fullName.substring(0, lastSpace), fullName.substring(lastSpace + 1)};
    }

    private String valueOr(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }
}
