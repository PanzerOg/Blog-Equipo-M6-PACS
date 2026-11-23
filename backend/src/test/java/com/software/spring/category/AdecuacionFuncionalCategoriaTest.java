package com.software.spring.category;

import com.software.spring.controller.VerAnuncioController;
import com.software.spring.model.Anuncio;
import com.software.spring.model.Mensaje;
import com.software.spring.repository.AnuncioRepository;
import com.software.spring.repository.MensajeRepository;
import com.software.spring.service.AnuncioService;
import com.software.spring.service.ChatService;
import com.software.spring.service.MensajeService;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

/**
 * Pruebas semilla categorizadas según las subcaracterísticas de Adecuación Funcional (ISO/IEC 25010).
 */
@Tag("categoria")
@ExtendWith(MockitoExtension.class)
class AdecuacionFuncionalCategoriaTest {

    @Mock
    private MensajeRepository mensajeRepository;

    @Mock
    private ChatService chatService;

    @Mock
    private AnuncioRepository anuncioRepository;

    @Mock
    private AnuncioService anuncioService;

    @Test
    @Tag("completitud")
    void completitud_mensajeService_enviaMensajeYActualizaUltimoMensajeDelChat() {
        MensajeService service = new MensajeService(mensajeRepository, chatService);
        Mensaje entrada = new Mensaje("Hola equipo", "user-2", null, null, 10);

        Mensaje enviado = service.enviarMensaje(entrada);

        assertNotNull(enviado.getId());
        assertNotNull(enviado.getFechaCreacion());
        assertEquals("Hola equipo", enviado.getContenido());
        assertEquals("user-2", enviado.getAutorId());
        assertEquals(10, enviado.getChatId());
        verify(mensajeRepository).save(any(Mensaje.class));
        verify(chatService).actualizarUltimoMensaje(10, "Hola equipo");
    }

    @Test
    @Tag("correccion")
    void correccion_anuncioService_rechazaTituloVacioSinPersistir() {
        AnuncioService service = new AnuncioService(anuncioRepository);
        Anuncio invalido = new Anuncio(null, "   ", "Contenido valido", "admin-1", null, null);

        assertThrows(IllegalArgumentException.class, () -> service.crearAnuncio(invalido));

        verifyNoInteractions(anuncioRepository);
    }

    @Test
    @Tag("pertinencia")
    void pertinencia_verAnuncioController_retorna404CuandoNoExiste() {
        VerAnuncioController controller = new VerAnuncioController(anuncioService);
        when(anuncioService.obtenerAnuncioPorId(12345)).thenReturn(Optional.empty());

        ResponseEntity<?> respuesta = controller.obtenerAnuncioPorId(12345);

        assertEquals(HttpStatus.NOT_FOUND, respuesta.getStatusCode());
    }
}
