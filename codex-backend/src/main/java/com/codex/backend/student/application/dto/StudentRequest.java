package com.codex.backend.student.application.dto;
import lombok.Data;

@Data
public class StudentRequest {
    private String studentCode;
    private String firstName;
    private String lastName;
    private String fullName;
    private String className;
    private String email;
}
