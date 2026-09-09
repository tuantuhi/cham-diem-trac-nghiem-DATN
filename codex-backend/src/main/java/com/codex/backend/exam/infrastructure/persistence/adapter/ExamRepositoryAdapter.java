package com.codex.backend.exam.infrastructure.persistence.adapter;
import com.codex.backend.exam.application.port.out.ExamRepositoryPort;
import com.codex.backend.exam.domain.entity.Exam;
import com.codex.backend.exam.infrastructure.persistence.entity.ExamJpaEntity;
import com.codex.backend.exam.infrastructure.persistence.repository.ExamJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ExamRepositoryAdapter implements ExamRepositoryPort {
    private final ExamJpaRepository jpaRepository;
    @Override
    public Exam save(Exam entity) {
        ExamJpaEntity jpaEntity = ExamJpaEntity.builder()
                .id(entity.getId())
                .title(entity.getTitle())
                .description(entity.getDescription())
                .subject(entity.getSubject())
                .examType(entity.getExamType())
                .answerKey(entity.getAnswerKey())
                .startTime(entity.getStartTime())
                .endTime(entity.getEndTime())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
        jpaRepository.save(jpaEntity);
        return entity;
    }
    @Override
    public Optional<Exam> findById(UUID id) {
        return jpaRepository.findById(id).map(this::toDomain);
    }

    @Override
    public List<Exam> findAll() {
        return jpaRepository.findAll().stream().map(this::toDomain).toList();
    }

    @Override
    public void deleteById(UUID id) {
        jpaRepository.deleteById(id);
    }

    private Exam toDomain(ExamJpaEntity e) {
        return Exam.builder()
                .id(e.getId())
                .title(e.getTitle())
                .description(e.getDescription())
                .subject(e.getSubject())
                .examType(e.getExamType())
                .answerKey(e.getAnswerKey())
                .startTime(e.getStartTime())
                .endTime(e.getEndTime())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt())
                .build();
    }
}
