package com.codex.backend.exam.application.dto;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class ExamRequest {
    private String title;
    private String description;
    private String subject;
    private String examType = "OMR_50";
    private String answerKey;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
}
