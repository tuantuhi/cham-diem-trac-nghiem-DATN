package com.codex.backend.result.application.port.in;
import com.codex.backend.result.application.dto.ResultRequest;
import com.codex.backend.result.application.dto.ResultResponse;
import java.util.List;
import java.util.UUID;
public interface ResultUseCase {
    ResultResponse create(ResultRequest request);
    ResultResponse getById(UUID id);
    List<ResultResponse> list();
}
