package com.codex.backend.result.application.dto;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class ResultRequest {
    private UUID studentId;
    private UUID examId;
    private UUID gradeId;
    private BigDecimal finalScore;
    private LocalDateTime publishedAt;
}
