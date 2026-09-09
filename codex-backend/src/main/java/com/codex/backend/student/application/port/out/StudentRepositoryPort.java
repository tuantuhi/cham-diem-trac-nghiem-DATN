package com.codex.backend.student.application.port.out;
import com.codex.backend.student.domain.entity.Student;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
public interface StudentRepositoryPort {
    Student save(Student entity);
    Optional<Student> findById(UUID id);
    List<Student> findAll();
    void deleteById(UUID id);
}
