package com.codex.backend.grading.presentation.controller;
import com.codex.backend.grading.application.dto.GradeRequest;
import com.codex.backend.grading.application.dto.GradeResponse;
import com.codex.backend.grading.application.port.in.GradeUseCase;
import com.codex.backend.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/gradings")
@RequiredArgsConstructor
public class GradeController {
    private final GradeUseCase useCase;
    @PostMapping
    public ResponseEntity<ApiResponse<GradeResponse>> create(@RequestBody GradeRequest request) {
        return ResponseEntity.ok(ApiResponse.success(useCase.create(request), "Created successfully"));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<GradeResponse>>> list() {
        return ResponseEntity.ok(ApiResponse.success(useCase.list(), "Fetched successfully"));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<GradeResponse>> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(ApiResponse.success(useCase.getById(id), "Fetched successfully"));
    }
}
