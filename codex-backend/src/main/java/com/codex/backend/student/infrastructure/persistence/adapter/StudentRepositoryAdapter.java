package com.codex.backend.student.infrastructure.persistence.adapter;
import com.codex.backend.student.application.port.out.StudentRepositoryPort;
import com.codex.backend.student.domain.entity.Student;
import com.codex.backend.student.infrastructure.persistence.entity.StudentJpaEntity;
import com.codex.backend.student.infrastructure.persistence.repository.StudentJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class StudentRepositoryAdapter implements StudentRepositoryPort {
    private final StudentJpaRepository jpaRepository;
    @Override
    public Student save(Student entity) {
        StudentJpaEntity jpaEntity = StudentJpaEntity.builder()
                .id(entity.getId())
                .userId(entity.getUserId())
                .studentCode(entity.getStudentCode())
                .firstName(entity.getFirstName())
                .lastName(entity.getLastName())
                .className(entity.getClassName())
                .email(entity.getEmail())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
        jpaRepository.save(jpaEntity);
        return entity;
    }
    @Override
    public Optional<Student> findById(UUID id) {
        return jpaRepository.findById(id).map(this::toDomain);
    }

    @Override
    public List<Student> findAll() {
        return jpaRepository.findAll().stream().map(this::toDomain).toList();
    }

    @Override
    public void deleteById(UUID id) {
        jpaRepository.deleteById(id);
    }

    private Student toDomain(StudentJpaEntity e) {
        return Student.builder()
                .id(e.getId())
                .userId(e.getUserId())
                .studentCode(e.getStudentCode())
                .firstName(e.getFirstName())
                .lastName(e.getLastName())
                .className(e.getClassName())
                .email(e.getEmail())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt())
                .build();
    }
}
