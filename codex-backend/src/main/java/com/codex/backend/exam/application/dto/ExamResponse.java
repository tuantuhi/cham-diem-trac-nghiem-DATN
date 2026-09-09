package com.codex.backend.exam.application.dto;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class ExamResponse {
    private UUID id;
    private String title;
    private String description;
    private String subject;
    private String examType;
    private String answerKey;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
