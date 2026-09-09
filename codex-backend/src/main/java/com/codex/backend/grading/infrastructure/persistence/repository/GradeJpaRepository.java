package com.codex.backend.grading.infrastructure.persistence.repository;
import com.codex.backend.grading.infrastructure.persistence.entity.GradeJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface GradeJpaRepository extends JpaRepository<GradeJpaEntity, UUID> {}
