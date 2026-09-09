package com.codex.backend.student.application.dto;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class StudentResponse {
    private UUID id;
    private String studentCode;
    private String firstName;
    private String lastName;
    private String fullName;
    private String className;
    private String email;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
