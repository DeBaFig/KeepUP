import pygame
import random
import time
import math

# --- Constantes ---
LARGURA = 800
ALTURA = 600
BASE_GRAVIDADE = 0.1
BASE_IMPULSO_CLIQUE = -10
BASE_TERMINAL_VELOCITY = 2

# --- Sprites (Estados Visuais) ---
ESTADO_ABERTOS = 0
ESTADO_CLICADO = 1
ESTADO_INTERMEDIARIO = 2
ESTADO_FECHADOS = 3

DURACAO_ABERTOS = 3.0
DURACAO_INTERMEDIARIO = 0.5
DURACAO_FECHADOS = 0.1
DURACAO_CLICADO = 0.5

# --- Classe do Balão ---


class Balao(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # --- 1. Carregamento e Preparação das Imagens ---
        tamanho_fallback = 100 
        cor_fallback = (255, 100, 100)
        img_fallback = pygame.Surface([tamanho_fallback, tamanho_fallback], pygame.SRCALPHA)
        pygame.draw.circle(img_fallback, cor_fallback, (tamanho_fallback // 2, tamanho_fallback // 2), tamanho_fallback // 2)

        self.sprites = {} 
        sprites_carregados_com_sucesso = True

        try:
            # NOVO: Carregamento com os nomes de constantes e arquivos atualizados
            self.sprites[ESTADO_ABERTOS] = pygame.image.load("movimento_olhos_abertos.png").convert_alpha()
            self.sprites[ESTADO_CLICADO] = pygame.image.load("movimento_ao_clicar.png").convert_alpha()
            self.sprites[ESTADO_INTERMEDIARIO] = pygame.image.load("movimento_olhos_intermediario.png").convert_alpha()
            self.sprites[ESTADO_FECHADOS] = pygame.image.load("movimento_olhos_fechados.png").convert_alpha()
        
        except pygame.error as e:
            print(f"Erro ao carregar sprites: {e}. Usando imagens de fallback (círculo vermelho).")
            sprites_carregados_com_sucesso = False

        if not sprites_carregados_com_sucesso:
            # NOVO: Loop sobre as novas constantes de estado
            for estado in [ESTADO_ABERTOS, ESTADO_CLICADO, ESTADO_INTERMEDIARIO, ESTADO_FECHADOS]:
                 self.sprites[estado] = img_fallback

        if not self.sprites:
             raise RuntimeError("Falha crítica: Não foi possível carregar ou criar nenhum sprite.")

        # --- 2. Inicialização de Estado e Temporizadores ---
        self.estado_visual = ESTADO_ABERTOS # NOVO: Estado inicial é ABERTOS
        self._intermediate_from = None
        self.last_click_time = time.time()
        self.last_state_change = time.time()
        
        # --- 3. Atributos de Status (Base) ---
        self.gravidade_mult = 1.0
        self.impulso_mult = 1.0
        self.tamanho_base = 100 
        self.tamanho_mult = 1.0
        
        self.velocidade_y = 0
        self.velocidade_x = 0
        self.friccao_x = 0.995 
        
        self._setup_appearance()
        self.reset()
        
    def _setup_appearance(self):
        tamanho_atual = int(self.tamanho_base * self.tamanho_mult)
        
        # NOVO: Fallback para ESTADO_ABERTOS se o estado atual não existir (segurança)
        original_image = self.sprites.get(self.estado_visual, self.sprites[ESTADO_ABERTOS])
        self.image = pygame.transform.scale(original_image, (tamanho_atual, tamanho_atual))
        
        center_x = self.rect.centerx if hasattr(self, 'rect') else LARGURA // 2
        center_y = self.rect.centery if hasattr(self, 'rect') else ALTURA // 4
        
        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)

    def _set_visual_state(self, novo_estado):
        if self.estado_visual != novo_estado:
            anterior = self.estado_visual
            self.estado_visual = novo_estado
            if novo_estado == ESTADO_INTERMEDIARIO:
                self._intermediate_from = anterior
            else:
                self._intermediate_from = None
            self.last_state_change = time.time()
            self._setup_appearance() 

    def reset(self):
        self.rect.centerx = LARGURA // 2
        self.rect.y = ALTURA // 4
        
        self.velocidade_y = random.uniform(-5, -2)
        self.velocidade_x = 0
        self.last_click_time = time.time() 
        self._set_visual_state(ESTADO_ABERTOS) # NOVO: Começa em ABERTOS
        
    def update(self):
        agora = time.time()

        gravidade_atual = BASE_GRAVIDADE * self.gravidade_mult
        self.velocidade_y += gravidade_atual

        terminal_velocity_atual = BASE_TERMINAL_VELOCITY * self.gravidade_mult
        if self.velocidade_y > terminal_velocity_atual:
            self.velocidade_y = terminal_velocity_atual

        self.velocidade_x *= self.friccao_x
        self.rect.y += self.velocidade_y
        self.rect.x += self.velocidade_x

        # Limites da tela: topo e lados
        if self.rect.top < 0:
            self.rect.top = 0
            if self.velocidade_y < 0:
                self.velocidade_y = 0

        if self.rect.left < 0:
            self.rect.left = 0
            if self.velocidade_x < 0:
                self.velocidade_x = 0

        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
            if self.velocidade_x > 0:
                self.velocidade_x = 0

        # Estado CLICADO tem precedência
        if self.estado_visual == ESTADO_CLICADO and (agora - self.last_click_time) > DURACAO_CLICADO:
            self._set_visual_state(ESTADO_ABERTOS)
            return

        tempo_no_estado = agora - self.last_state_change

        if self.estado_visual == ESTADO_ABERTOS:
            if tempo_no_estado >= DURACAO_ABERTOS:
                self._set_visual_state(ESTADO_INTERMEDIARIO)

        elif self.estado_visual == ESTADO_INTERMEDIARIO:
            if tempo_no_estado >= DURACAO_INTERMEDIARIO:
                if self._intermediate_from == ESTADO_ABERTOS:
                    self._set_visual_state(ESTADO_FECHADOS)
                elif self._intermediate_from == ESTADO_FECHADOS:
                    self._set_visual_state(ESTADO_ABERTOS)
                else:
                    self._set_visual_state(ESTADO_FECHADOS)

        elif self.estado_visual == ESTADO_FECHADOS:
            if tempo_no_estado >= DURACAO_FECHADOS:
                self._set_visual_state(ESTADO_INTERMEDIARIO)

    def rebater(self):
        """
        Aplica impulso ao balão após clique:
        - componente vertical para cima (-impulso)
        - componente horizontal aleatória com ângulo entre 0° e 45°
        - se estiver na parede esquerda, força só para a direita
        - se estiver na parede direita, força só para a esquerda
        """
        impulso = abs(BASE_IMPULSO_CLIQUE) * self.impulso_mult
        self.velocidade_y = -impulso

        at_left = self.rect.left <= 0
        at_right = self.rect.right >= LARGURA

        if at_left and not at_right:
            sinal = 1
        elif at_right and not at_left:
            sinal = -1
        else:
            sinal = random.choice([-1, 1])

        ang_deg = random.uniform(0, 45)
        ang_rad = math.radians(ang_deg)
        vx = math.tan(ang_rad) * impulso
        self.velocidade_x = sinal * vx

        self.last_click_time = time.time()
        self._set_visual_state(ESTADO_CLICADO)
        
    def foi_clicado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)