package com.codex.backend.result.infrastructure.persistence.adapter;
import com.codex.backend.result.application.port.out.ResultRepositoryPort;
import com.codex.backend.result.domain.entity.Result;
import com.codex.backend.result.infrastructure.persistence.entity.ResultJpaEntity;
import com.codex.backend.result.infrastructure.persistence.repository.ResultJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ResultRepositoryAdapter implements ResultRepositoryPort {
    private final ResultJpaRepository jpaRepository;
    @Override
    public Result save(Result entity) {
        ResultJpaEntity jpaEntity = ResultJpaEntity.builder()
                .id(entity.getId())
                .studentId(entity.getStudentId())
                .examId(entity.getExamId())
                .gradeId(entity.getGradeId())
                .finalScore(entity.getFinalScore())
                .publishedAt(entity.getPublishedAt())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
        jpaRepository.save(jpaEntity);
        return entity;
    }
    @Override
    public Optional<Result> findById(UUID id) {
        return jpaRepository.findById(id).map(this::toDomain);
    }

    @Override
    public List<Result> findAll() {
        return jpaRepository.findAll().stream().map(this::toDomain).toList();
    }

    @Override
    public Optional<Result> findByExamIdAndStudentId(UUID examId, UUID studentId) {
        return jpaRepository.findByExamIdAndStudentId(examId, studentId).map(this::toDomain);
    }

    private Result toDomain(ResultJpaEntity e) {
        return Result.builder()
                .id(e.getId())
                .studentId(e.getStudentId())
                .examId(e.getExamId())
                .gradeId(e.getGradeId())
                .finalScore(e.getFinalScore())
                .publishedAt(e.getPublishedAt())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt())
                .build();
    }
}
