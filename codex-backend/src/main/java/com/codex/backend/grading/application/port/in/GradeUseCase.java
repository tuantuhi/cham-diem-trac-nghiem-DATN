package com.codex.backend.grading.application.port.in;
import com.codex.backend.grading.application.dto.GradeRequest;
import com.codex.backend.grading.application.dto.GradeResponse;
import java.util.List;
import java.util.UUID;
public interface GradeUseCase {
    GradeResponse create(GradeRequest request);
    GradeResponse getById(UUID id);
    List<GradeResponse> list();
}
