package com.codex.backend.submission.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Submission {
    private UUID id;
    private UUID examId;
    private UUID studentId;
    private String examCode;
    private String imageUrl;
    private BigDecimal score;
    private String status;
    private String content;
    private LocalDateTime submittedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
