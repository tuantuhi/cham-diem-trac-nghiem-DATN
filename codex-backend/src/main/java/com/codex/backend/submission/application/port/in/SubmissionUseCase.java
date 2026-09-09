package com.codex.backend.submission.application.port.in;
import com.codex.backend.submission.application.dto.SubmissionRequest;
import com.codex.backend.submission.application.dto.SubmissionResponse;
import java.util.List;
import java.util.UUID;
public interface SubmissionUseCase {
    SubmissionResponse create(SubmissionRequest request);
    SubmissionResponse getById(UUID id);
    List<SubmissionResponse> list();
    SubmissionResponse grade(UUID id);
}
