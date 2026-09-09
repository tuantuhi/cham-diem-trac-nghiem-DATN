package com.codex.backend.submission.infrastructure.persistence.adapter;
import com.codex.backend.submission.application.port.out.SubmissionRepositoryPort;
import com.codex.backend.submission.domain.entity.Submission;
import com.codex.backend.submission.infrastructure.persistence.entity.SubmissionJpaEntity;
import com.codex.backend.submission.infrastructure.persistence.repository.SubmissionJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.domain.Sort;
@Component
@RequiredArgsConstructor
public class SubmissionRepositoryAdapter implements SubmissionRepositoryPort {
    private final SubmissionJpaRepository jpaRepository;
    @Override
    public Submission save(Submission entity) {
        SubmissionJpaEntity jpaEntity = SubmissionJpaEntity.builder()
                .id(entity.getId())
                .examId(entity.getExamId())
                .studentId(entity.getStudentId())
                .examCode(entity.getExamCode())
                .imageUrl(entity.getImageUrl())
                .score(entity.getScore())
                .status(entity.getStatus())
                .content(entity.getContent())
                .submittedAt(entity.getSubmittedAt())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
        jpaRepository.save(jpaEntity);
        return entity;
    }
    @Override
    public Optional<Submission> findById(UUID id) {
        return jpaRepository.findById(id).map(this::toDomain);
    }

    @Override
    public List<Submission> findAll() {
        
        return jpaRepository.findAll(Sort.by(Sort.Direction.DESC, "createdAt"))
                .stream()
                .map(this::toDomain)
                .toList();
    }

    @Override
    public List<Submission> findByExamIdAndStudentId(UUID examId, UUID studentId) {
        return jpaRepository.findByExamIdAndStudentIdOrderByCreatedAtAsc(examId, studentId).stream().map(this::toDomain).toList();
    }

    private Submission toDomain(SubmissionJpaEntity e) {
        return Submission.builder()
                .id(e.getId())
                .examId(e.getExamId())
                .studentId(e.getStudentId())
                .examCode(e.getExamCode())
                .imageUrl(e.getImageUrl())
                .score(e.getScore())
                .status(e.getStatus())
                .content(e.getContent())
                .submittedAt(e.getSubmittedAt())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt())
                .build();
    }
}
