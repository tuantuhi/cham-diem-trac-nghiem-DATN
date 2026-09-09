package com.codex.backend.submission.application.port.out;

import java.util.List;
import java.util.Map;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.multipart.MultipartFile;

@FeignClient(name = "aiServiceClient", url = "${ai.service.url:http://localhost:8000}")
public interface AiServiceClient {

    @PostMapping(value = "/predict/omr", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    Map<String, Object> predictOmr50(@RequestPart("file") MultipartFile file);

    @PostMapping(value = "/predict/omr_20", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    Map<String, Object> predictOmr20(@RequestPart("file") MultipartFile file);

    @PostMapping(value = "/predict/yolo", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    Map<String, Object> predictYolo(@RequestPart("file") MultipartFile file);

    @PostMapping(value = "/predict/yolo/batch", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    Map<String, Object> predictYoloBatch(@RequestPart("files") List<MultipartFile> files);
}
