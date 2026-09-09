package com.codex.backend.student.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.UUID;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Student {
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
