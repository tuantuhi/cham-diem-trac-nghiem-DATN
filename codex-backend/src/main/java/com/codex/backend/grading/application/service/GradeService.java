package com.codex.backend.grading.application.service;
import com.codex.backend.grading.application.dto.GradeRequest;
import com.codex.backend.grading.application.dto.GradeResponse;
import com.codex.backend.grading.application.port.in.GradeUseCase;
import com.codex.backend.grading.application.port.out.GradeRepositoryPort;
import com.codex.backend.grading.domain.entity.Grade;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class GradeService implements GradeUseCase {
    private final GradeRepositoryPort repositoryPort;
    @Override
    public GradeResponse create(GradeRequest request) {
        LocalDateTime now = LocalDateTime.now();
        Grade grade = Grade.builder()
                .id(UUID.randomUUID())
                .submissionId(request.getSubmissionId())
                .score(request.getScore() == null ? BigDecimal.ZERO : request.getScore())
                .feedback(request.getFeedback())
                .gradedBy(request.getGradedBy())
                .createdAt(now)
                .updatedAt(now)
                .build();
        return toResponse(repositoryPort.save(grade));
    }
    @Override
    public GradeResponse getById(UUID id) {
        return repositoryPort.findById(id).map(this::toResponse).orElseThrow();
    }

    @Override
    public List<GradeResponse> list() {
        return repositoryPort.findAll().stream().map(this::toResponse).toList();
    }

    private GradeResponse toResponse(Grade grade) {
        GradeResponse response = new GradeResponse();
        response.setId(grade.getId());
        response.setSubmissionId(grade.getSubmissionId());
        response.setScore(grade.getScore());
        response.setFeedback(grade.getFeedback());
        response.setGradedBy(grade.getGradedBy());
        response.setCreatedAt(grade.getCreatedAt());
        response.setUpdatedAt(grade.getUpdatedAt());
        return response;
    }
}
