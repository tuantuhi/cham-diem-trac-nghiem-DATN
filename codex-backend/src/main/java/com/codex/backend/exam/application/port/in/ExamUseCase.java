package com.codex.backend.exam.application.port.in;
import com.codex.backend.exam.application.dto.ExamRequest;
import com.codex.backend.exam.application.dto.ExamResponse;
import java.util.List;
import java.util.UUID;
public interface ExamUseCase {
    ExamResponse create(ExamRequest request);
    ExamResponse getById(UUID id);
    List<ExamResponse> list();
    ExamResponse update(UUID id, ExamRequest request);
    void delete(UUID id);
    ExamResponse updateAnswerKey(UUID id, String answerKey);
}
