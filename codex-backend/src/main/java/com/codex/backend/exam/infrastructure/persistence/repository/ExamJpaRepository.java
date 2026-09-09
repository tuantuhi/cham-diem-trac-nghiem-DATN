package com.codex.backend.exam.infrastructure.persistence.repository;
import com.codex.backend.exam.infrastructure.persistence.entity.ExamJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface ExamJpaRepository extends JpaRepository<ExamJpaEntity, UUID> {}
