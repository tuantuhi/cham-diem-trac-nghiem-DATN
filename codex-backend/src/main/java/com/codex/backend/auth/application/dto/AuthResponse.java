package com.codex.backend.auth.application.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class AuthResponse {
    private String id;
    private String token;
    private String username;
    private String role;
    private String email;
}
