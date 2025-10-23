import pygame
import random
import math # Mantido para compatibilidade com a lógica diagonal anterior (se você usá-la)
import time # NOVO: Necessário para controle de tempo

# --- Constantes ---
LARGURA = 800
ALTURA = 600
BASE_GRAVIDADE = 0.1
BASE_IMPULSO_CLIQUE = -15
BASE_TERMINAL_VELOCITY = 5 # Usando um valor mais razoável para a queda

# --- Sprites (Estados Visuais) ---
# Definindo constantes para os estados visuais (facilita a leitura)
ESTADO_CAINDO = 0     # Padrão, caindo (HiPaint_1761180755849.png)
ESTADO_CLICADO = 1    # No momento exato do clique (HiPaint_1761180779789.png)
ESTADO_SUBINDO = 2    # Após o meio segundo de clique, subindo (HiPaint_1761180762900.png)
ESTADO_ENTEDIADO = 3  # Parado por 3s (HiPaint_1761180771287.png)

# --- Classe do Balão ---
class Balao(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # --- 1. Carregamento e Preparação das Imagens ---
        # Certifique-se de que esses arquivos PNG estão no mesmo diretório do seu código!
        try:
            self.sprites = {
                ESTADO_CAINDO: pygame.image.load("HiPaint_1761180755849.png").convert_alpha(),
                ESTADO_CLICADO: pygame.image.load("HiPaint_1761180779789.png").convert_alpha(),
                ESTADO_SUBINDO: pygame.image.load("HiPaint_1761180762900.png").convert_alpha(),
                ESTADO_ENTEDIADO: pygame.image.load("HiPaint_1761180771287.png").convert_alpha(),
            }
        except pygame.error as e:
            print(f"Erro ao carregar sprites: {e}")
            # Use um círculo de cor sólida como fallback se as imagens falharem
            tamanho = 50
            cor = (255, 100, 100)
            img_fallback = pygame.Surface([tamanho, tamanho], pygame.SRCALPHA)
            pygame.draw.circle(img_fallback, cor, (tamanho // 2, tamanho // 2), tamanho // 2)
            for key in self.sprites:
                self.sprites[key] = img_fallback
        
        # --- 2. Inicialização de Estado e Temporizadores ---
        self.estado_visual = ESTADO_CAINDO
        self.last_click_time = time.time()
        self.last_state_change = time.time()
        
        # --- 3. Atributos de Status (Base) ---
        self.gravidade_mult = 1.0
        self.impulso_mult = 1.0
        self.tamanho_base = 100 # Tamanho base ajustado para as imagens
        self.tamanho_mult = 1.0
        
        # Variáveis de física
        self.velocidade_y = 0
        self.velocidade_x = 0
        self.friccao_x = 0.995 # (Ajuste se estiver usando a física diagonal)
        
        # Configura a aparência inicial
        self._setup_appearance()
        self.reset()
        
    def _setup_appearance(self):
        """Redimensiona o sprite atual e ajusta o rect."""
        tamanho_atual = int(self.tamanho_base * self.tamanho_mult)
        
        # Pega a imagem do estado atual e redimensiona
        original_image = self.sprites.get(self.estado_visual, self.sprites[ESTADO_CAINDO])
        self.image = pygame.transform.scale(original_image, (tamanho_atual, tamanho_atual))
        
        # Armazena a posição central antes de recalcular o rect
        center_x = self.rect.centerx if hasattr(self, 'rect') else LARGURA // 2
        center_y = self.rect.centery if hasattr(self, 'rect') else ALTURA // 4
        
        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)

    def _set_visual_state(self, novo_estado):
        """Altera o estado visual e atualiza o sprite, se necessário."""
        if self.estado_visual != novo_estado:
            self.estado_visual = novo_estado
            self.last_state_change = time.time()
            self._setup_appearance() # Redesenha com o novo sprite

    def reset(self):
        """Reinicia a posição, velocidade e estado do balão."""
        self.rect.centerx = LARGURA // 2
        self.rect.y = ALTURA // 4
        
        self.velocidade_y = random.uniform(-5, -2)
        self.velocidade_x = 0
        self.last_click_time = time.time() # Reseta o tempo de inatividade
        self._set_visual_state(ESTADO_SUBINDO) # Começa subindo
        
    def update(self):
        agora = time.time()

        # 1. Lógica de Física (movimento e gravidade)
        gravidade_atual = BASE_GRAVIDADE * self.gravidade_mult
        self.velocidade_y += gravidade_atual
        
        terminal_velocity_atual = BASE_TERMINAL_VELOCITY * self.gravidade_mult
        
        if self.velocidade_y > terminal_velocity_atual:
            self.velocidade_y = terminal_velocity_atual
        
        # (Lógica de fricção e limites X e Y, omitida para brevidade, mas deve estar aqui)
        self.velocidade_x *= self.friccao_x # (Se estiver usando movimento diagonal)
        self.rect.y += self.velocidade_y
        self.rect.x += self.velocidade_x

        # 2. Lógica de Transição de Estado Visual
        
        # A. Fim do ESTADO_CLICADO (0.5s) -> ESTADO_SUBINDO
        if self.estado_visual == ESTADO_CLICADO and (agora - self.last_click_time) > 0.5:
            self._set_visual_state(ESTADO_SUBINDO)
        
        # B. Transição de ESTADO_SUBINDO para ESTADO_CAINDO
        # ESTADO_SUBINDO dura enquanto a velocidade é negativa (está subindo)
        if self.estado_visual == ESTADO_SUBINDO and self.velocidade_y >= 0:
            self._set_visual_state(ESTADO_CAINDO)
        
        # C. Transição de ESTADO_CAINDO/SUBINDO para ESTADO_ENTEDIADO (3s sem clique)
        # O estado entediado só ocorre se não estiver subindo (velocidade_y < 0) ou clicado.
        if (agora - self.last_click_time) > 3.0:
            # Garante que o balão só "fique entediado" quando estiver caindo ou parado
            if self.estado_visual not in [ESTADO_CLICADO, ESTADO_SUBINDO]:
                 self._set_visual_state(ESTADO_ENTEDIADO)

        # D. Sai do ESTADO_ENTEDIADO quando é clicado ou começa a cair
        if self.estado_visual == ESTADO_ENTEDIADO and self.velocidade_y >= 0:
            self._set_visual_state(ESTADO_CAINDO)


    def rebater(self):
        """Aplica o impulso para cima e atualiza o estado visual."""
        
        # Lógica de Física
        impulso_clique_atual = BASE_IMPULSO_CLIQUE * self.impulso_mult
        self.velocidade_y = impulso_clique_atual
        # (Lógica de impulso diagonal X, omitida para brevidade, mas deve estar aqui)
        
        # Lógica de Estado Visual
        self.last_click_time = time.time()
        self._set_visual_state(ESTADO_CLICADO)
        
    # Os métodos rebater, aplicar_upgrade e foi_clicado permanecem iguais na lógica.

    def foi_clicado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)