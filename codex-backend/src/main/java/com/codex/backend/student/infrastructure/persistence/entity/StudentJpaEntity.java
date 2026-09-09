package com.codex.backend.student.infrastructure.persistence.entity;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "students")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StudentJpaEntity {
    @Id
    private UUID id;
    private UUID userId;
    private String studentCode;
    private String firstName;
    private String lastName;
    private String className;
    private String email;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
