package com.codex.backend.auth.infrastructure.persistence.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "users")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserJpaEntity {
    @Id
    private UUID id;
    private String username;
    private String email;
    private String password;
    private String role;
    private String provider;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
