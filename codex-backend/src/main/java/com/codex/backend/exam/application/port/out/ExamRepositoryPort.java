package com.codex.backend.exam.application.port.out;
import com.codex.backend.exam.domain.entity.Exam;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
public interface ExamRepositoryPort {
    Exam save(Exam entity);
    Optional<Exam> findById(UUID id);
    List<Exam> findAll();
    void deleteById(UUID id);
}
