package com.codex.backend.submission.application.port.out;
import com.codex.backend.submission.domain.entity.Submission;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
public interface SubmissionRepositoryPort {
    Submission save(Submission entity);
    Optional<Submission> findById(UUID id);
    List<Submission> findAll();
    List<Submission> findByExamIdAndStudentId(UUID examId, UUID studentId);
}
