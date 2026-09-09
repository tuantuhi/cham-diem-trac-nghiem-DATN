package com.codex.backend.auth.application.port.in;

import com.codex.backend.auth.application.dto.AuthRequest;
import com.codex.backend.auth.application.dto.AuthResponse;

public interface AuthUseCase {
    AuthResponse register(AuthRequest request);
    AuthResponse login(AuthRequest request);
}
