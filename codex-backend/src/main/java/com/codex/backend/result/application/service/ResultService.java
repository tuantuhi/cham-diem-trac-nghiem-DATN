package com.codex.backend.result.application.service;
import com.codex.backend.result.application.dto.ResultRequest;
import com.codex.backend.result.application.dto.ResultResponse;
import com.codex.backend.result.application.port.in.ResultUseCase;
import com.codex.backend.result.application.port.out.ResultRepositoryPort;
import com.codex.backend.result.domain.entity.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ResultService implements ResultUseCase {
    private final ResultRepositoryPort repositoryPort;
    @Override
    public ResultResponse create(ResultRequest request) {
        LocalDateTime now = LocalDateTime.now();
        Result result = Result.builder()
                .id(UUID.randomUUID())
                .studentId(request.getStudentId())
                .examId(request.getExamId())
                .gradeId(request.getGradeId())
                .finalScore(request.getFinalScore() == null ? BigDecimal.ZERO : request.getFinalScore())
                .publishedAt(request.getPublishedAt() == null ? now : request.getPublishedAt())
                .createdAt(now)
                .updatedAt(now)
                .build();
        return toResponse(repositoryPort.save(result));
    }
    @Override
    public ResultResponse getById(UUID id) {
        return repositoryPort.findById(id).map(this::toResponse).orElseThrow();
    }

    @Override
    public List<ResultResponse> list() {
        return repositoryPort.findAll().stream().map(this::toResponse).toList();
    }

    private ResultResponse toResponse(Result result) {
        ResultResponse response = new ResultResponse();
        response.setId(result.getId());
        response.setStudentId(result.getStudentId());
        response.setExamId(result.getExamId());
        response.setGradeId(result.getGradeId());
        response.setFinalScore(result.getFinalScore());
        response.setPublishedAt(result.getPublishedAt());
        response.setCreatedAt(result.getCreatedAt());
        response.setUpdatedAt(result.getUpdatedAt());
        return response;
    }
}
