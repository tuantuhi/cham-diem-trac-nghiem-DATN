package com.codex.backend.grading.infrastructure.persistence.adapter;
import com.codex.backend.grading.application.port.out.GradeRepositoryPort;
import com.codex.backend.grading.domain.entity.Grade;
import com.codex.backend.grading.infrastructure.persistence.entity.GradeJpaEntity;
import com.codex.backend.grading.infrastructure.persistence.repository.GradeJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class GradeRepositoryAdapter implements GradeRepositoryPort {
    private final GradeJpaRepository jpaRepository;
    @Override
    public Grade save(Grade entity) {
        GradeJpaEntity jpaEntity = GradeJpaEntity.builder()
                .id(entity.getId())
                .submissionId(entity.getSubmissionId())
                .score(entity.getScore())
                .feedback(entity.getFeedback())
                .gradedBy(entity.getGradedBy())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
        jpaRepository.save(jpaEntity);
        return entity;
    }
    @Override
    public Optional<Grade> findById(UUID id) {
        return jpaRepository.findById(id).map(this::toDomain);
    }

    @Override
    public List<Grade> findAll() {
        return jpaRepository.findAll().stream().map(this::toDomain).toList();
    }

    private Grade toDomain(GradeJpaEntity e) {
        return Grade.builder()
                .id(e.getId())
                .submissionId(e.getSubmissionId())
                .score(e.getScore())
                .feedback(e.getFeedback())
                .gradedBy(e.getGradedBy())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt())
                .build();
    }
}
