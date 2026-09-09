package com.codex.backend.exam.presentation.controller;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.codex.backend.exam.application.dto.ExamRequest;
import com.codex.backend.exam.application.dto.ExamResponse;
import com.codex.backend.exam.application.port.in.ExamUseCase;
import com.codex.backend.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/exams")
@RequiredArgsConstructor
public class ExamController {
    private final ExamUseCase useCase;
    private final ObjectMapper objectMapper;

    @PostMapping
    public ResponseEntity<ApiResponse<ExamResponse>> create(@RequestBody ExamRequest request) {
        return ResponseEntity.ok(ApiResponse.success(useCase.create(request), "Created successfully"));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<ExamResponse>>> list() {
        return ResponseEntity.ok(ApiResponse.success(useCase.list(), "Fetched successfully"));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<ExamResponse>> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(ApiResponse.success(useCase.getById(id), "Fetched successfully"));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<ExamResponse>> update(@PathVariable UUID id, @RequestBody ExamRequest request) {
        return ResponseEntity.ok(ApiResponse.success(useCase.update(id, request), "Updated successfully"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable UUID id) {
        useCase.delete(id);
        return ResponseEntity.ok(ApiResponse.success(null, "Deleted successfully"));
    }

    @PostMapping("/{id}/answer-keys")
    public ResponseEntity<ApiResponse<ExamResponse>> saveAnswerKey(@PathVariable UUID id, @RequestBody Object answerKey) throws JsonProcessingException {
        String payload = answerKey instanceof String ? (String) answerKey : objectMapper.writeValueAsString(answerKey);
        return ResponseEntity.ok(ApiResponse.success(useCase.updateAnswerKey(id, payload), "Answer key saved"));
    }

    @GetMapping("/{id}/answer-keys")
    public ResponseEntity<ApiResponse<String>> getAnswerKey(@PathVariable UUID id) {
        return ResponseEntity.ok(ApiResponse.success(useCase.getById(id).getAnswerKey(), "Fetched successfully"));
    }
}
