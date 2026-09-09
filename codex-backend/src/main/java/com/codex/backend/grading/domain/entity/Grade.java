package com.codex.backend.grading.domain.entity;

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
public class Grade {
    private UUID id;
    private UUID submissionId;
    private BigDecimal score;
    private String feedback;
    private UUID gradedBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
