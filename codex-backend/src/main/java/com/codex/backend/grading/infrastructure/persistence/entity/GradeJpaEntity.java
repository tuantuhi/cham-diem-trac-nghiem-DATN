package com.codex.backend.grading.infrastructure.persistence.entity;
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
@Table(name = "grades")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GradeJpaEntity {
    @Id
    private UUID id;
    private UUID submissionId;
    private BigDecimal score;
    private String feedback;
    private UUID gradedBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
