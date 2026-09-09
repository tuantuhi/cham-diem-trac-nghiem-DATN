package com.codex.backend.submission.application.dto;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class SubmissionResponse {
    private UUID id;
    private UUID examId;
    private UUID studentId;
    private String examCode;
    private String imageUrl;
    private String status;
    private BigDecimal score;
    private String content;
    private LocalDateTime submittedAt;
}
