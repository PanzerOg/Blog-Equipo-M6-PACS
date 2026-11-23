package com.software.spring.service;

import com.software.spring.model.Comentario;
import com.software.spring.repository.ComentarioRepository;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

/**
 * Pruebas unitarias semilla para validar la ejecución aislada con Mockito bajo la etiqueta "unitaria".
 */
@Tag("unitaria")
@ExtendWith(MockitoExtension.class)
class ComentarioServiceUnitTest {

    @Mock
    private ComentarioRepository comentarioRepository;

    @Test
    void crearComentario_conContenidoValido_persisteYRetornaComentario() {
        ComentarioService service = new ComentarioService(comentarioRepository);
        LocalDateTime fecha = LocalDateTime.of(2026, 11, 23, 18, 0);
        Comentario entrada = new Comentario(null, "Excelente aporte al blog", "user-1", 42, fecha);

        when(comentarioRepository.save(any(Comentario.class))).thenAnswer(inv -> inv.getArgument(0));

        Comentario resultado = service.crearComentario(entrada);

        assertNotNull(resultado.getId());
        assertEquals("Excelente aporte al blog", resultado.getContenido());
        assertEquals("user-1", resultado.getAutor());
        assertEquals(42, resultado.getPublicacionId());
        assertEquals(fecha, resultado.getFechaCreacion());
        verify(comentarioRepository).save(any(Comentario.class));
    }

    @Test
    void crearComentario_conContenidoVacio_lanzaExcepcionYNoPersiste() {
        ComentarioService service = new ComentarioService(comentarioRepository);
        Comentario entrada = new Comentario(null, "   ", "user-1", 42, LocalDateTime.now());

        assertThrows(IllegalArgumentException.class, () -> service.crearComentario(entrada));

        verifyNoInteractions(comentarioRepository);
    }

    @Test
    void editarComentario_porAutorDistinto_lanzaExcepcionYNoGuarda() {
        ComentarioService service = new ComentarioService(comentarioRepository);
        Comentario existente = new Comentario(10, "Texto original", "autor-original", 42, LocalDateTime.now());

        when(comentarioRepository.findAll()).thenReturn(List.of(existente));

        assertThrows(IllegalArgumentException.class,
                () -> service.editarComentario(10, "Texto editado", "otro-usuario"));

        verify(comentarioRepository, never()).save(any());
    }
}
