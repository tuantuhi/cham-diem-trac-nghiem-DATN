package com.codex.backend.auth.presentation.controller;

import com.codex.backend.auth.application.dto.AuthRequest;
import com.codex.backend.auth.application.dto.AuthResponse;
import com.codex.backend.auth.application.port.in.AuthUseCase;
import com.codex.backend.auth.application.port.out.UserRepositoryPort;
import com.codex.backend.auth.domain.entity.User;
import com.codex.backend.auth.infrastructure.security.JwtUtil;
import com.codex.backend.common.dto.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthUseCase authUseCase;
    private final JwtUtil jwtUtil;
    private final UserRepositoryPort userRepositoryPort;

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<AuthResponse>> register(@RequestBody @Valid AuthRequest request) {
        AuthResponse response = authUseCase.register(request);
        return ResponseEntity.ok(ApiResponse.success(response, "User registered successfully"));
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AuthResponse>> login(@RequestBody @Valid AuthRequest request) {
        AuthResponse response = authUseCase.login(request);
        return ResponseEntity.ok(ApiResponse.success(response, "Login successful"));
    }

    @PostMapping("/refresh")
    public ResponseEntity<ApiResponse<AuthResponse>> refresh(@RequestHeader("Authorization") String authorization) {
        String token = authorization.replace("Bearer ", "");
        String username = jwtUtil.extractUsername(token);
        User user = userRepositoryPort.findByUsername(username).orElseThrow();
        String refreshed = jwtUtil.generateToken(user.getUsername(), user.getRole());
        return ResponseEntity.ok(ApiResponse.success(toResponse(user, refreshed), "Token refreshed"));
    }

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<AuthResponse>> me(Authentication authentication) {
        User user = userRepositoryPort.findByUsername(authentication.getName()).orElseThrow();
        return ResponseEntity.ok(ApiResponse.success(toResponse(user, null), "Current user"));
    }

    private AuthResponse toResponse(User user, String token) {
        return new AuthResponse(user.getId().toString(), token, user.getUsername(), user.getRole(), user.getEmail());
    }
}
