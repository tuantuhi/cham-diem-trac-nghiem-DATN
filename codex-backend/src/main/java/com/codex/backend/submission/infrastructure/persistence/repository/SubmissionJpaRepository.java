package com.codex.backend.submission.infrastructure.persistence.repository;
import com.codex.backend.submission.infrastructure.persistence.entity.SubmissionJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;
public interface SubmissionJpaRepository extends JpaRepository<SubmissionJpaEntity, UUID> {
    List<SubmissionJpaEntity> findByExamIdAndStudentIdOrderByCreatedAtAsc(UUID examId, UUID studentId);
}
