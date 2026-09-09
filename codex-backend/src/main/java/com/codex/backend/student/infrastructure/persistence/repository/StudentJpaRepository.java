package com.codex.backend.student.infrastructure.persistence.repository;
import com.codex.backend.student.infrastructure.persistence.entity.StudentJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;
public interface StudentJpaRepository extends JpaRepository<StudentJpaEntity, UUID> {}
