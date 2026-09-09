package com.codex.backend.submission.infrastructure.persistence.entity;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "submissions")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionJpaEntity {
    @Id
    private UUID id;
    private UUID examId;
    private UUID studentId;
    private String examCode;
    private String imageUrl;
    private BigDecimal score;
    private String status;
    @jakarta.persistence.Column(columnDefinition = "TEXT")
    private String content;
    private LocalDateTime submittedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
