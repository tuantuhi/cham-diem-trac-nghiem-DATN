package com.codex.backend.grading.application.dto;
import lombok.Data;
import java.math.BigDecimal;
import java.util.UUID;

@Data
public class GradeRequest {
    private UUID submissionId;
    private BigDecimal score;
    private String feedback;
    private UUID gradedBy;
}
