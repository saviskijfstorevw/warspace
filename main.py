import pygame
import random
import time
import asyncio  # Necessário para rodar no navegador

# Inicializando o Pygame
pygame.init()

# Definindo cores
BRANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
PRETO = (0, 0, 0)

# Tamanho da tela
LARGURA_TELA = 800
ALTURA_TELA = 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Jogo de Ação - Warspace")

# FPS
clock = pygame.time.Clock()
FPS = 60

# Carregando as imagens (com fallback caso não encontre os arquivos)
try:
    player_img = pygame.image.load("img/foguete.png")
    player_img = pygame.transform.scale(player_img, (50, 50))
except:
    player_img = pygame.Surface((50, 50))
    player_img.fill(AZUL)

try:
    enemy_img = pygame.image.load("img/ufo.png")
    enemy_img = pygame.transform.scale(enemy_img, (50, 50))
except:
    enemy_img = pygame.Surface((50, 50))
    enemy_img.fill(VERMELHO)

bullet_img = pygame.Surface((10, 5))
bullet_img.fill(VERDE)

enemy_bullet_img = pygame.Surface((10, 5))
enemy_bullet_img.fill(VERMELHO) 

try:
    meteoro_img = pygame.image.load("img/meteoro.png")
    meteoro_img = pygame.transform.scale(meteoro_img, (30, 30))
except:
    meteoro_img = pygame.Surface((30, 30))
    meteoro_img.fill((150, 150, 150))

try:
    fundo_img = pygame.image.load("img/fundo.png")
    fundo_img = pygame.transform.scale(fundo_img, (LARGURA_TELA, ALTURA_TELA))
except:
    fundo_img = None

# Classe do jogador
class Player:
    def __init__(self):
        self.x = 100
        self.y = ALTURA_TELA // 2
        self.velocidade = 5
        self.vidas = 3
        self.ultimo_tiro = 0  

    def mover(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.velocidade
        if keys[pygame.K_RIGHT] and self.x < LARGURA_TELA - 50:
            self.x += self.velocidade
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.velocidade
        if keys[pygame.K_DOWN] and self.y < ALTURA_TELA - 50:
            self.y += self.velocidade

    def desenhar(self):
        tela.blit(player_img, (self.x, self.y))

    def pode_disparar(self, intervalo=0.3):
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_tiro >= intervalo:
            self.ultimo_tiro = tempo_atual
            return True
        return False

# Classe do inimigo
class Enemy:
    def __init__(self):
        self.x = LARGURA_TELA - 100
        self.y = random.randint(50, ALTURA_TELA - 100)
        self.velocidade = 2
        self.vida = 150  
        self.ultimo_tiro = 0  

    def mover(self):
        self.y += self.velocidade
        if self.y >= ALTURA_TELA - 50 or self.y <= 0:
            self.velocidade = -self.velocidade

    def disparar(self):
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_tiro >= random.uniform(0.5, 1.5):  
            self.ultimo_tiro = tempo_atual
            pos_y_tiro = self.y + random.randint(-20, 20)
            return Bullet(self.x - 10, pos_y_tiro, -15)
        return None

    def desenhar(self):
        tela.blit(enemy_img, (self.x, self.y))

    def mostrar_vida(self):
        font = pygame.font.SysFont("Arial", 20)
        texto = font.render(f'Vida: {self.vida}', True, BRANCO)
        tela.blit(texto, (self.x, self.y - 30)) 

# Classe do meteoro
class Meteoro:
    def __init__(self):
        self.x = LARGURA_TELA  
        self.y = random.randint(0, ALTURA_TELA - 30)
        self.velocidade_x = -random.randint(3, 6)
        self.velocidade_y = random.choice([0, 1, -1])

    def mover(self):
        self.x += self.velocidade_x
        self.y += self.velocidade_y

    def desenhar(self):
        tela.blit(meteoro_img, (self.x, self.y))

    def colisao(self, player):
        if player.x < self.x + 30 and player.x + 50 > self.x and player.y < self.y + 30 and player.y + 50 > self.y:
            return True
        return False

    def colisao_tiro(self, tiro):
        if self.x < tiro.x < self.x + 30 and self.y < tiro.y < self.y + 30:
            return True
        return False

# Classe do tiro
class Bullet:
    def __init__(self, x, y, velocidade):
        self.x = x
        self.y = y
        self.velocidade = velocidade

    def mover(self):
        self.x += self.velocidade

    def desenhar(self):
        tela.blit(bullet_img, (self.x, self.y))

# Funções auxiliares de interface
def desenhar_texto(msg, cor, pos_x, pos_y, tamanho=30):
    font = pygame.font.SysFont("Arial", tamanho)
    texto_surface = font.render(msg, True, cor)
    tela.blit(texto_surface, (pos_x, pos_y))

def desenhar_botao(texto, x, y, largura, altura, cor_fundo, cor_texto):
    pygame.draw.rect(tela, cor_fundo, (x, y, largura, altura))
    desenhar_texto(texto, cor_texto, x + largura // 2 - len(texto) * 10 // 2, y + altura // 3)

def verificar_clique_botao(mx, my, x, y, largura, altura):
    if x < mx < x + largura and y < my < y + altura:
        return True
    return False

def reiniciar_jogo():
    player = Player()
    enemy = Enemy()
    meteoros = [Meteoro() for _ in range(8)]  
    tiros = []
    tiros_inimigo = []
    return player, enemy, meteoros, tiros, tiros_inimigo

# Função principal assíncrona para compatibilidade Web
async def jogo():
    player, enemy, meteoros, tiros, tiros_inimigo = reiniciar_jogo()
    pausado = False
    game_over = False
    vitoria = False
    estado_jogo = "inicio"  

    while True:
        # Captura de eventos de clique do mouse
        clique_detectado = False
        mx, my = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            if evento.type == pygame.MOUSEBUTTONDOWN:
                clique_detectado = True

        keys = pygame.key.get_pressed()

        # Pressionar R para reiniciar o jogo
        if keys[pygame.K_r] and game_over:
            player, enemy, meteoros, tiros, tiros_inimigo = reiniciar_jogo()
            game_over = False
            vitoria = False
            estado_jogo = "jogo"

        # Sistema de Telas / Estados do Jogo
        if estado_jogo == "inicio":
            tela.fill(PRETO)
            desenhar_botao("Iniciar Jogo", LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 - 50, 200, 50, AZUL, BRANCO)

            if clique_detectado:
                if verificar_clique_botao(mx, my, LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 - 50, 200, 50):
                    estado_jogo = "jogo"

        elif estado_jogo == "jogo":
            if not pausado and not game_over:
                player.mover(keys)

                if keys[pygame.K_SPACE] and player.pode_disparar():
                    tiros.append(Bullet(player.x + 50, player.y + 20, 10))

                enemy.mover()

                tiro_inimigo = enemy.disparar()
                if tiro_inimigo:
                    tiros_inimigo.append(tiro_inimigo)

                # Movimentação dos tiros do jogador
                for tiro in tiros[:]:
                    tiro.mover()
                    if tiro.x > LARGURA_TELA:
                        tiros.remove(tiro)

                # Movimentação dos tiros do inimigo
                for t_inimigo in tiros_inimigo[:]:
                    t_inimigo.mover()
                    if t_inimigo.x < 0:
                        tiros_inimigo.remove(t_inimigo)

                # Dano no inimigo
                for tiro in tiros[:]:
                    if enemy.x < tiro.x < enemy.x + 50 and enemy.y < tiro.y < enemy.y + 50:
                        enemy.vida -= 10
                        tiros.remove(tiro)
                        if enemy.vida <= 0:
                            vitoria = True
                            game_over = True

                # Tiro destrói meteoro
                for meteoro in meteoros[:]:
                    for tiro in tiros[:]:
                        if meteoro.colisao_tiro(tiro):
                            meteoros.remove(meteoro)
                            tiros.remove(tiro)
                            break

                # Colisão direta: Jogador vs Inimigo
                if player.x < enemy.x + 50 and player.x + 50 > enemy.x and player.y < enemy.y + 50 and player.y + 50 > enemy.y:
                    player.vidas -= 1
                    if player.vidas <= 0:
                        game_over = True

                # Jogador atingido por tiro inimigo
                for t_inimigo in tiros_inimigo[:]:
                    if player.x < t_inimigo.x < player.x + 50 and player.y < t_inimigo.y < player.y + 50:
                        player.vidas -= 1
                        tiros_inimigo.remove(t_inimigo)
                        if player.vidas <= 0:
                            game_over = True

                # Movimentação e colisão dos meteoros
                for meteoro in meteoros[:]:
                    meteoro.mover()
                    if meteoro.x < 0 or meteoro.y < 0 or meteoro.y > ALTURA_TELA:
                        meteoros.remove(meteoro)
                        continue

                    if meteoro.colisao(player):
                        player.vidas -= 1
                        meteoros.remove(meteoro)
                        if player.vidas <= 0:
                            game_over = True

                # Mantém a quantidade de meteoros na tela
                while len(meteoros) < 8:
                    meteoros.append(Meteoro())

            # Renderização dos elementos do jogo
            if fundo_img:
                tela.blit(fundo_img, (0, 0))
            else:
                tela.fill(PRETO)

            player.desenhar()
            enemy.desenhar()
            enemy.mostrar_vida()

            for meteoro in meteoros:
                meteoro.desenhar()

            for tiro in tiros:
                tiro.desenhar()

            for t_inimigo in tiros_inimigo:
                tela.blit(enemy_bullet_img, (t_inimigo.x, t_inimigo.y))

            desenhar_texto(f'Vidas: {player.vidas}', BRANCO, 10, 10)

            # Tela de Fim de Jogo (Game Over / Vitória)
            if game_over:
                if vitoria:
                    desenhar_texto("Você Venceu!", BRANCO, LARGURA_TELA // 2 - 80, ALTURA_TELA // 2 - 30, 40)
                else:
                    desenhar_texto("Game Over!", BRANCO, LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 - 50, 40)

                desenhar_botao("Reiniciar", LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 + 20, 200, 50, AZUL, BRANCO)

                if clique_detectado:
                    if verificar_clique_botao(mx, my, LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 + 20, 200, 50):
                        player, enemy, meteoros, tiros, tiros_inimigo = reiniciar_jogo()
                        game_over = False
                        vitoria = False

        pygame.display.update()
        clock.tick(FPS)
        
        # Linha crucial para o Pygbag manter a aba do navegador respondendo
        await asyncio.sleep(0)

# Inicializa o loop assíncrono
asyncio.run(jogo())