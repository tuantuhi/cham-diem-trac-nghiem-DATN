package com.codex.backend.student.presentation.controller;
import com.codex.backend.student.application.dto.StudentRequest;
import com.codex.backend.student.application.dto.StudentResponse;
import com.codex.backend.student.application.port.in.StudentUseCase;
import com.codex.backend.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/students")
@RequiredArgsConstructor
public class StudentController {
    private final StudentUseCase useCase;
    @PostMapping
    public ResponseEntity<ApiResponse<StudentResponse>> create(@RequestBody StudentRequest request) {
        return ResponseEntity.ok(ApiResponse.success(useCase.create(request), "Created successfully"));
    }

    @PostMapping("/import")
    public ResponseEntity<ApiResponse<List<StudentResponse>>> importStudents(@RequestBody List<StudentRequest> request) {
        return ResponseEntity.ok(ApiResponse.success(useCase.importStudents(request), "Imported successfully"));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<StudentResponse>>> list() {
        return ResponseEntity.ok(ApiResponse.success(useCase.list(), "Fetched successfully"));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<StudentResponse>> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(ApiResponse.success(useCase.getById(id), "Fetched successfully"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable UUID id) {
        useCase.delete(id);
        return ResponseEntity.ok(ApiResponse.success(null, "Deleted successfully"));
    }
}
