package com.codex.backend.submission.presentation.controller;
import com.codex.backend.submission.application.dto.SubmissionRequest;
import com.codex.backend.submission.application.dto.SubmissionResponse;
import com.codex.backend.submission.application.port.in.SubmissionUseCase;
import com.codex.backend.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/submissions")
@RequiredArgsConstructor
public class SubmissionController {
    private final SubmissionUseCase useCase;

    @PostMapping(consumes = {"multipart/form-data"})
    public ResponseEntity<ApiResponse<SubmissionResponse>> create(
            @RequestParam("files") List<org.springframework.web.multipart.MultipartFile> files,
            @RequestParam("examId") UUID examId,
            @RequestParam("studentId") UUID studentId) {
        SubmissionRequest request = new SubmissionRequest();
        request.setFiles(files);
        request.setExamId(examId);
        request.setStudentId(studentId);
        return ResponseEntity.ok(ApiResponse.success(useCase.create(request), "Created successfully"));
    }

    @PostMapping(value = "/upload", consumes = {"multipart/form-data"})
    public ResponseEntity<ApiResponse<SubmissionResponse>> upload(
            @RequestParam("files") List<org.springframework.web.multipart.MultipartFile> files,
            @RequestParam("examId") UUID examId,
            @RequestParam("studentId") UUID studentId) {
        return create(files, examId, studentId);
    }

    @PostMapping("/grade")
    public ResponseEntity<ApiResponse<SubmissionResponse>> grade(@RequestParam("submissionId") UUID submissionId) {
        return ResponseEntity.ok(ApiResponse.success(useCase.grade(submissionId), "Graded successfully"));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<SubmissionResponse>>> list() {
        return ResponseEntity.ok(ApiResponse.success(useCase.list(), "Fetched successfully"));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<SubmissionResponse>> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(ApiResponse.success(useCase.getById(id), "Fetched successfully"));
    }
}
