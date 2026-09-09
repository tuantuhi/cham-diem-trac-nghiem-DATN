package com.codex.backend.result.infrastructure.persistence.entity;
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
@Table(name = "results")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResultJpaEntity {
    @Id
    private UUID id;
    private UUID studentId;
    private UUID examId;
    private UUID gradeId;
    private BigDecimal finalScore;
    private LocalDateTime publishedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
