package com.codex.backend.grading.application.dto;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class GradeResponse {
    private UUID id;
    private UUID submissionId;
    private BigDecimal score;
    private String feedback;
    private UUID gradedBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
