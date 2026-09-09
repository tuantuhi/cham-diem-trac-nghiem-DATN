package com.codex.backend.result.presentation.controller;
import com.codex.backend.result.application.dto.ResultRequest;
import com.codex.backend.result.application.dto.ResultResponse;
import com.codex.backend.result.application.port.in.ResultUseCase;
import com.codex.backend.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/results")
@RequiredArgsConstructor
public class ResultController {
    private final ResultUseCase useCase;
    @PostMapping
    public ResponseEntity<ApiResponse<ResultResponse>> create(@RequestBody ResultRequest request) {
        return ResponseEntity.ok(ApiResponse.success(useCase.create(request), "Created successfully"));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<ResultResponse>>> list() {
        return ResponseEntity.ok(ApiResponse.success(useCase.list(), "Fetched successfully"));
    }

    @GetMapping("/export/excel")
    public ResponseEntity<String> exportExcel() {
        String header = "id,studentId,examId,gradeId,finalScore,publishedAt\n";
        String rows = useCase.list().stream()
                .map(r -> String.join(",",
                        safe(r.getId()),
                        safe(r.getStudentId()),
                        safe(r.getExamId()),
                        safe(r.getGradeId()),
                        safe(r.getFinalScore()),
                        safe(r.getPublishedAt())))
                .collect(Collectors.joining("\n"));
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=exam_results.csv")
                .contentType(MediaType.parseMediaType("text/csv"))
                .body(header + rows);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<ResultResponse>> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(ApiResponse.success(useCase.getById(id), "Fetched successfully"));
    }

    private String safe(Object value) {
        return value == null ? "" : value.toString();
    }
}
