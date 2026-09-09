package com.codex.backend.result.application.dto;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class ResultResponse {
    private UUID id;
    private UUID studentId;
    private UUID examId;
    private UUID gradeId;
    private BigDecimal finalScore;
    private LocalDateTime publishedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
