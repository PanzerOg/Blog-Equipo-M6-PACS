package com.software.spring.integration;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.software.spring.model.Comentario;
import com.software.spring.repository.JsonComentarioRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Pruebas de integración semilla con perfil "test" (sin tocar backend/data) bajo la etiqueta "integracion".
 */
@Tag("integracion")
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class AnuncioFlowIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Value("${app.anunciosPath}")
    private String anunciosPath;

    @BeforeEach
    void limpiarDatosDePrueba() throws Exception {
        Path path = Paths.get(anunciosPath);
        if (path.getParent() != null) {
            Files.createDirectories(path.getParent());
        }
        Files.writeString(path, "[]", StandardCharsets.UTF_8);
    }

    @Test
    void obtenerAnuncioActivo_sinDatos_retornaNoContent() throws Exception {
        mockMvc.perform(get("/api/anuncio"))
                .andExpect(status().isNoContent());
    }

    @Test
    void crearYConsultarAnuncio_flujoCompletoApiYPersistenciaJson() throws Exception {
        String payload = """
                {
                  "titulo": "Mantenimiento Programado",
                  "contenido": "El sistema se actualizara el domingo a las 22:00.",
                  "autorId": "admin-1"
                }
                """;

        MvcResult createResult = mockMvc.perform(post("/api/anuncio/crear")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").isNumber())
                .andExpect(jsonPath("$.titulo").value("Mantenimiento Programado"))
                .andReturn();

        JsonNode body = objectMapper.readTree(createResult.getResponse().getContentAsString());
        int createdId = body.get("id").asInt();

        mockMvc.perform(get("/api/anuncio/{id}", createdId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.titulo").value("Mantenimiento Programado"))
                .andExpect(jsonPath("$.contenido").value("El sistema se actualizara el domingo a las 22:00."));

        int nonexistentId = createdId == 999999 ? 999998 : 999999;
        mockMvc.perform(get("/api/anuncio/{id}", nonexistentId))
                .andExpect(status().isNotFound());
    }

    @Test
    void jsonComentarioRepository_enDirectorioTemporal_persisteYElimina(@TempDir Path tempDir) {
        JsonComentarioRepository repository = new JsonComentarioRepository(
                objectMapper,
                tempDir.resolve("comentarios.json").toString()
        );

        Comentario comentario = new Comentario(701, "Comentario persistido", "autor-7", 55, LocalDateTime.now());
        repository.save(comentario);

        List<Comentario> encontrados = repository.findByPublicacionId(55);
        assertEquals(1, encontrados.size());
        assertEquals("Comentario persistido", encontrados.get(0).getContenido());

        repository.deleteById(701);
        assertTrue(repository.findByPublicacionId(55).isEmpty());
    }
}
