package com.codex.backend.submission.application.service;

import com.codex.backend.exam.application.port.out.ExamRepositoryPort;
import com.codex.backend.exam.domain.entity.Exam;
import com.codex.backend.submission.application.dto.SubmissionRequest;
import com.codex.backend.submission.application.dto.SubmissionResponse;
import com.codex.backend.submission.application.port.in.SubmissionUseCase;
import com.codex.backend.submission.application.port.out.AiServiceClient;
import com.codex.backend.submission.application.port.out.SubmissionRepositoryPort;
import com.codex.backend.submission.domain.entity.Submission;
import com.codex.backend.result.application.port.out.ResultRepositoryPort;
import com.codex.backend.result.domain.entity.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

@Service
@RequiredArgsConstructor
public class SubmissionService implements SubmissionUseCase {
    private final SubmissionRepositoryPort submissionRepositoryPort;
    private final ExamRepositoryPort examRepositoryPort;
    private final ResultRepositoryPort resultRepositoryPort;
    private final AiServiceClient aiServiceClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public SubmissionResponse create(SubmissionRequest request) {
        Exam exam = examRepositoryPort.findById(request.getExamId())
                .orElseThrow(() -> new RuntimeException("Exam not found"));

        if (request.getFiles() == null || request.getFiles().isEmpty()) {
            throw new RuntimeException("No files uploaded");
        }

        UUID submissionId = UUID.randomUUID();
        // Save images to local directory or MinIO (Mocking saving by just generating a mock folder URL)
        String imageUrl = "/uploads/" + submissionId + "/";

        // Call AI Service based on Exam Type
        Map<String, Object> aiResultRaw;
        String examType = exam.getExamType() != null ? exam.getExamType() : "OMR_50";

        long startTime = System.currentTimeMillis();
        try {
            switch (examType) {
                case "OMR_20":
                    aiResultRaw = aiServiceClient.predictOmr20(request.getFiles().get(0));
                    break;
                case "YOLO":
                    if (request.getFiles().size() > 1) {
                        aiResultRaw = aiServiceClient.predictYoloBatch(request.getFiles());
                    } else {
                        aiResultRaw = aiServiceClient.predictYolo(request.getFiles().get(0));
                    }
                    break;
                case "OMR_50":
                default:
                    aiResultRaw = aiServiceClient.predictOmr50(request.getFiles().get(0));
                    break;
            }
        } catch (Exception e) {
            aiResultRaw = Map.of(
                    "examCode", examType,
                    "answers", Map.of(),
                    "confidence", 0,
                    "warning", "AI Service unavailable: " + e.getMessage()
            );
        }
        long endTime = System.currentTimeMillis();

        Map<String, Object> aiResult = new java.util.HashMap<>(aiResultRaw);
        aiResult.put("executionTime", endTime - startTime);

        BigDecimal imageScore = calculateScore(exam.getAnswerKey(), aiResult);
            String status = aiResult.containsKey("warning") ? "FAILED" : "DONE";

        // Save Submission
        Submission submission = Submission.builder()
                .id(submissionId)
                .examId(request.getExamId())
                .studentId(request.getStudentId())
                .examCode(String.valueOf(aiResult.getOrDefault("examCode", examType)))
                .imageUrl(imageUrl)
                .score(imageScore)
                .status(status)
                .content(toJson(aiResult))
                .submittedAt(LocalDateTime.now())
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        submissionRepositoryPort.save(submission);

        return toResponse(submission);
    }

    @Override
    public SubmissionResponse getById(UUID id) {
        return submissionRepositoryPort.findById(id).map(this::toResponse).orElseThrow();
    }

    @Override
    public List<SubmissionResponse> list() {
        return submissionRepositoryPort.findAll().stream().map(this::toResponse).toList();
    }

    @Override
    public SubmissionResponse grade(UUID id) {
        Submission submission = submissionRepositoryPort.findById(id)
                .orElseThrow(() -> new RuntimeException("Submission not found"));

        Exam exam = examRepositoryPort.findById(submission.getExamId())
                .orElseThrow(() -> new RuntimeException("Exam not found"));

        // Aggregate all submissions for this examId and studentId
        List<Submission> previousSubmissions = submissionRepositoryPort.findByExamIdAndStudentId(submission.getExamId(), submission.getStudentId());
        
        Map<String, String> aggregatedAnswers = new java.util.HashMap<>();
        long totalExecutionTime = 0;
        
        for (Submission sub : previousSubmissions) {
            if ("DONE".equals(sub.getStatus()) && sub.getContent() != null) {
                try {
                    Map<String, Object> contentMap = objectMapper.readValue(sub.getContent(), new TypeReference<Map<String, Object>>() {});
                    Object answersObj = contentMap.containsKey("results") ? contentMap.get("results") : contentMap.get("answers");
                    if (answersObj != null) {
                        Map<String, String> answers = objectMapper.convertValue(answersObj, new TypeReference<Map<String, String>>() {});
                        aggregatedAnswers.putAll(answers);
                    }
                    if (contentMap.containsKey("executionTime")) {
                        totalExecutionTime += ((Number) contentMap.get("executionTime")).longValue();
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
        
        Map<String, Object> aggregatedAiResult = new java.util.HashMap<>();
        aggregatedAiResult.put("answers", aggregatedAnswers);
        aggregatedAiResult.put("executionTime", totalExecutionTime);
        BigDecimal finalScore = calculateScore(exam.getAnswerKey(), aggregatedAiResult);
        
        Result result = resultRepositoryPort.findByExamIdAndStudentId(submission.getExamId(), submission.getStudentId())
            .map(existing -> Result.builder()
                    .id(existing.getId())
                    .studentId(existing.getStudentId())
                    .examId(existing.getExamId())
                    .gradeId(existing.getGradeId())
                    .finalScore(finalScore)
                    .publishedAt(LocalDateTime.now())
                    .createdAt(existing.getCreatedAt())
                    .updatedAt(LocalDateTime.now())
                    .build())
            .orElseGet(() -> Result.builder()
                    .id(UUID.randomUUID())
                    .studentId(submission.getStudentId())
                    .examId(submission.getExamId())
                    .finalScore(finalScore)
                    .publishedAt(LocalDateTime.now())
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build());
                    
        resultRepositoryPort.save(result);

        // Update the return response with the final score and aggregated answers so the frontend can display it
        SubmissionResponse response = toResponse(submission);
        response.setScore(finalScore);
        response.setContent(toJson(aggregatedAiResult));
        
        return response;
    }

    private BigDecimal calculateScore(String answerKey, Map<String, Object> aiResult) {
        if (answerKey == null || answerKey.isBlank()) {
            return BigDecimal.ZERO;
        }

        Object answersObj = aiResult.containsKey("results") ? aiResult.get("results") : aiResult.get("answers");
        if (answersObj == null) {
            return BigDecimal.ZERO;
        }

        try {
            Map<String, String> keyMap = objectMapper.readValue(answerKey, new TypeReference<Map<String, String>>() {});
            Map<String, String> studentAnswers = objectMapper.convertValue(answersObj, new TypeReference<Map<String, String>>() {});

            if (keyMap.isEmpty()) return BigDecimal.ZERO;

            int correctCount = 0;
            for (Map.Entry<String, String> entry : keyMap.entrySet()) {
                String qNum = entry.getKey();
                String correctAns = entry.getValue();
                String studentAns = studentAnswers.get(qNum);
                
                if (correctAns != null && correctAns.equalsIgnoreCase(studentAns)) {
                    correctCount++;
                }
            }

            BigDecimal score = BigDecimal.valueOf(correctCount)
                    .multiply(BigDecimal.TEN)
                    .divide(BigDecimal.valueOf(keyMap.size()), 2, RoundingMode.HALF_UP);
            return score;
        } catch (Exception e) {
            e.printStackTrace();
            return BigDecimal.ZERO;
        }
    }

    private String toJson(Object obj) {
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (Exception e) {
            e.printStackTrace();
            return "{}";
        }
    }

    private SubmissionResponse toResponse(Submission submission) {
        SubmissionResponse response = new SubmissionResponse();
        response.setId(submission.getId());
        response.setExamId(submission.getExamId());
        response.setStudentId(submission.getStudentId());
        response.setExamCode(submission.getExamCode());
        response.setImageUrl(submission.getImageUrl());
        response.setScore(submission.getScore());
        response.setStatus(submission.getStatus());
        response.setContent(submission.getContent());
        response.setSubmittedAt(submission.getSubmittedAt());
        return response;
    }
}
