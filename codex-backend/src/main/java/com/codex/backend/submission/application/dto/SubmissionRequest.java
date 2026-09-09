package com.codex.backend.submission.application.dto;
import lombok.Data;
import org.springframework.web.multipart.MultipartFile;
import java.util.UUID;
import java.util.List;

@Data
public class SubmissionRequest {
    private List<MultipartFile> files;
    private UUID examId;
    private UUID studentId;
}
