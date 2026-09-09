package com.codex.backend.auth.application.service;

import com.codex.backend.auth.application.dto.AuthRequest;
import com.codex.backend.auth.application.dto.AuthResponse;
import com.codex.backend.auth.application.port.in.AuthUseCase;
import com.codex.backend.auth.application.port.out.UserRepositoryPort;
import com.codex.backend.auth.domain.entity.User;
import com.codex.backend.auth.infrastructure.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService implements AuthUseCase {

    private final UserRepositoryPort userRepositoryPort;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Override
    public AuthResponse register(AuthRequest request) {
        if (userRepositoryPort.findByUsername(request.getUsername()).isPresent()) {
            throw new RuntimeException("Username is already taken");
        }

        User user = User.builder()
                .id(UUID.randomUUID())
                .username(request.getUsername())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .role(normalizeRole(request.getRole()))
                .provider("local")
                .createdAt(LocalDateTime.now())
                .build();

        User savedUser = userRepositoryPort.save(user);
        String token = jwtUtil.generateToken(savedUser.getUsername(), savedUser.getRole());

        return toResponse(savedUser, token);
    }

    @Override
    public AuthResponse login(AuthRequest request) {
        User user = userRepositoryPort.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("Invalid username or password"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid username or password");
        }

        String token = jwtUtil.generateToken(user.getUsername(), user.getRole());

        return toResponse(user, token);
    }

    private AuthResponse toResponse(User user, String token) {
        return new AuthResponse(user.getId().toString(), token, user.getUsername(), user.getRole(), user.getEmail());
    }

    private String normalizeRole(String role) {
        if (role == null || role.isBlank()) {
            return "ROLE_TEACHER";
        }
        return role.startsWith("ROLE_") ? role : "ROLE_" + role.toUpperCase();
    }
}
