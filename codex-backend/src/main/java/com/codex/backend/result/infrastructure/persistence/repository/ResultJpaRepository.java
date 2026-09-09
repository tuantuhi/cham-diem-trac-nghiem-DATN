package com.codex.backend.result.infrastructure.persistence.repository;
import com.codex.backend.result.infrastructure.persistence.entity.ResultJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.UUID;
public interface ResultJpaRepository extends JpaRepository<ResultJpaEntity, UUID> {
    Optional<ResultJpaEntity> findByExamIdAndStudentId(UUID examId, UUID studentId);
}
