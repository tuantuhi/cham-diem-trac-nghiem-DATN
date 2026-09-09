package com.codex.backend.exam.application.service;
import com.codex.backend.exam.application.dto.ExamRequest;
import com.codex.backend.exam.application.dto.ExamResponse;
import com.codex.backend.exam.application.port.in.ExamUseCase;
import com.codex.backend.exam.application.port.out.ExamRepositoryPort;
import com.codex.backend.exam.domain.entity.Exam;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ExamService implements ExamUseCase {
    private final ExamRepositoryPort repositoryPort;

    @Override
    public ExamResponse create(ExamRequest request) {
        LocalDateTime now = LocalDateTime.now();
        Exam exam = Exam.builder()
                .id(UUID.randomUUID())
                .title(request.getTitle())
                .description(request.getDescription())
                .subject(request.getSubject())
                .examType(request.getExamType() == null ? "OMR_50" : request.getExamType())
                .answerKey(request.getAnswerKey())
                .startTime(request.getStartTime() == null ? now : request.getStartTime())
                .endTime(request.getEndTime() == null ? now.plusHours(2) : request.getEndTime())
                .createdAt(now)
                .updatedAt(now)
                .build();
        return toResponse(repositoryPort.save(exam));
    }

    @Override
    public ExamResponse getById(UUID id) {
        return repositoryPort.findById(id).map(this::toResponse).orElseThrow();
    }

    @Override
    public List<ExamResponse> list() {
        return repositoryPort.findAll().stream().map(this::toResponse).toList();
    }

    @Override
    public ExamResponse update(UUID id, ExamRequest request) {
        Exam current = repositoryPort.findById(id).orElseThrow();
        Exam updated = Exam.builder()
                .id(current.getId())
                .title(valueOr(request.getTitle(), current.getTitle()))
                .description(valueOr(request.getDescription(), current.getDescription()))
                .subject(valueOr(request.getSubject(), current.getSubject()))
                .examType(valueOr(request.getExamType(), current.getExamType()))
                .answerKey(valueOr(request.getAnswerKey(), current.getAnswerKey()))
                .startTime(request.getStartTime() == null ? current.getStartTime() : request.getStartTime())
                .endTime(request.getEndTime() == null ? current.getEndTime() : request.getEndTime())
                .createdAt(current.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();
        return toResponse(repositoryPort.save(updated));
    }

    @Override
    public void delete(UUID id) {
        repositoryPort.deleteById(id);
    }

    @Override
    public ExamResponse updateAnswerKey(UUID id, String answerKey) {
        Exam current = repositoryPort.findById(id).orElseThrow();
        Exam updated = Exam.builder()
                .id(current.getId())
                .title(current.getTitle())
                .description(current.getDescription())
                .subject(current.getSubject())
                .examType(current.getExamType())
                .answerKey(answerKey)
                .startTime(current.getStartTime())
                .endTime(current.getEndTime())
                .createdAt(current.getCreatedAt())
                .updatedAt(LocalDateTime.now())
                .build();
        return toResponse(repositoryPort.save(updated));
    }

    private ExamResponse toResponse(Exam exam) {
        ExamResponse response = new ExamResponse();
        response.setId(exam.getId());
        response.setTitle(exam.getTitle());
        response.setDescription(exam.getDescription());
        response.setSubject(exam.getSubject());
        response.setExamType(exam.getExamType());
        response.setAnswerKey(exam.getAnswerKey());
        response.setStartTime(exam.getStartTime());
        response.setEndTime(exam.getEndTime());
        response.setCreatedAt(exam.getCreatedAt());
        response.setUpdatedAt(exam.getUpdatedAt());
        return response;
    }

    private String valueOr(String value, String fallback) {
        return value == null ? fallback : value;
    }
}
