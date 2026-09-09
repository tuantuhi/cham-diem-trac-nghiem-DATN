package com.codex.backend.result.application.port.out;
import com.codex.backend.result.domain.entity.Result;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
public interface ResultRepositoryPort {
    Result save(Result entity);
    Optional<Result> findById(UUID id);
    List<Result> findAll();
    Optional<Result> findByExamIdAndStudentId(UUID examId, UUID studentId);
}
