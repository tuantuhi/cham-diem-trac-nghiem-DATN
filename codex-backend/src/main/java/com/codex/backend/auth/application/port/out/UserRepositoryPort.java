package com.codex.backend.auth.application.port.out;

import com.codex.backend.auth.domain.entity.User;
import java.util.Optional;
import java.util.UUID;

public interface UserRepositoryPort {
    User save(User user);
    Optional<User> findByUsername(String username);
    Optional<User> findById(UUID id);
}
