package com.codex.backend.grading.application.port.out;
import com.codex.backend.grading.domain.entity.Grade;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
public interface GradeRepositoryPort {
    Grade save(Grade entity);
    Optional<Grade> findById(UUID id);
    List<Grade> findAll();
}
