import pygame
import math
import random
import sys

# ==========================================
# 配置与常量
# ==========================================
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

# --- 拟物化军用计算机配色 ---
# 机箱外壳
C_CHASSIS = (32, 35, 30)
C_CHASSIS_DARK = (22, 25, 20)
C_CHASSIS_TEXTURE = (38, 42, 34)

# 金属面板（3D凸起效果）
C_METAL_FACE = (72, 76, 62)
C_METAL_HIGHLIGHT = (115, 120, 100)
C_METAL_SHADOW = (38, 42, 30)
C_METAL_EDGE = (55, 60, 48)

# 面板内陷开口（设备开口）
C_RECESS = (15, 17, 13)
C_RECESS_BORDER = (40, 44, 34)
C_RECESS_SHADOW = (8, 10, 6)

# CRT显示器边框（厚重橡胶/塑料）
C_CRT_BEZEL = (20, 22, 18)
C_CRT_BEZEL_HIGHLIGHT = (50, 52, 45)
C_CRT_BEZEL_SHADOW = (10, 12, 8)
C_CRT_GLASS = (6, 8, 5)

# 油漆文字色（刻在金属上的标签）
C_TEXT_MAIN = (205, 210, 190)
C_TEXT_DIM = (110, 115, 95)
C_TEXT_LABEL = (170, 175, 155)

# 荧光磷光色（仅CRT屏幕内部）
C_PHOSPHOR_GREEN = (80, 255, 120)
C_PHOSPHOR_GREEN_DIM = (40, 120, 60)
C_PHOSPHOR_AMBER = (255, 210, 80)
C_PHOSPHOR_AMBER_DIM = (140, 110, 30)
C_PHOSPHOR_RED = (255, 80, 60)
C_PHOSPHOR_RED_DIM = (130, 40, 30)
C_PHOSPHOR_CYAN = (60, 220, 255)
C_PHOSPHOR_CYAN_DIM = (30, 110, 130)

# P-18 雷达 (琥珀色磷光 CRT)
C_P18_BG = (6, 5, 2)
C_P18_GRID = (90, 70, 20)
C_P18_SWEEP = (255, 220, 90)
C_P18_BLIP = (255, 240, 130)
C_P18_MISSILE = (255, 190, 90)
C_P18_AFTERGLOW = (220, 180, 60)

# 火控雷达 (绿色磷光 CRT)
C_FCR_BG = (3, 10, 5)
C_FCR_GRID = (25, 70, 35)
C_FCR_STROBE = (100, 255, 160)
C_FCR_TARGET = (120, 255, 120)
C_FCR_MISSILE = (255, 255, 140)
C_FCR_NOISE = (15, 45, 25)
C_FCR_SCAN = (60, 200, 90)

# TV光学 (绿色夜视 CRT)
C_TV_SKY = (18, 42, 22)
C_TV_GROUND = (10, 26, 14)
C_TV_RETICLE = (100, 255, 100)

# 指示灯（物理灯泡）
C_LAMP_OFF = (30, 35, 28)
C_LAMP_RED = (255, 50, 50)
C_LAMP_GREEN = (80, 255, 100)
C_LAMP_YELLOW = (255, 230, 60)
C_LAMP_ORANGE = (255, 160, 30)

# 终端/菜单（纯CRT文字界面）
C_TERM_BG = (8, 10, 7)
C_TERM_GREEN = (80, 255, 120)
C_TERM_CYAN = (60, 220, 255)
C_TERM_RED = (255, 80, 60)
C_TERM_YELLOW = (255, 255, 100)
C_TERM_DIM = (40, 70, 50)

# --- 状态枚举 ---
STATE_MENU = 0
STATE_BRIEFING = 1
STATE_SIMULATION = 2
STATE_DEBRIEFING = 3
STATE_MANUAL = 4

SCENARIO_DRONE = 0
SCENARIO_F4E = 1
SCENARIO_F117 = 2

GUIDANCE_LEAD = 0
GUIDANCE_THREE_POINT = 1

# ==========================================
# 辅助函数
# ==========================================

def normalize_angle(angle):
    return angle % 360

def get_angle_diff(a, b):
    diff = (a - b + 180) % 360 - 180
    return diff

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

def draw_metal_panel(surface, rect, title=""):
    """绘制拟物化金属面板 - 苏联军用计算机风格"""
    x, y, w, h = rect
    inset = 6
    
    # 底部阴影（厚度）
    pygame.draw.rect(surface, C_METAL_SHADOW, (x+2, y+2, w, h), border_radius=3)
    # 主体金属面
    pygame.draw.rect(surface, C_METAL_FACE, (x, y, w, h), border_radius=3)
    # 左上高光（3D凸起）
    pygame.draw.line(surface, C_METAL_HIGHLIGHT, (x+1, y+h-2), (x+1, y+1), 2)
    pygame.draw.line(surface, C_METAL_HIGHLIGHT, (x+1, y+1), (x+w-2, y+1), 2)
    # 右下阴影（3D凸起）
    pygame.draw.line(surface, C_METAL_SHADOW, (x+w-1, y+1), (x+w-1, y+h-2), 2)
    pygame.draw.line(surface, C_METAL_SHADOW, (x+1, y+h-1), (x+w-2, y+h-1), 2)
    
    # 内陷开口（设备面板内部）
    inner = (x + inset, y + inset, w - inset*2, h - inset*2)
    pygame.draw.rect(surface, C_RECESS, inner, border_radius=2)
    # 开口边缘（上左亮，下右暗）
    pygame.draw.line(surface, C_RECESS_BORDER, (x+inset, y+h-inset), (x+inset, y+inset), 1)
    pygame.draw.line(surface, C_RECESS_BORDER, (x+inset, y+inset), (x+w-inset, y+inset), 1)
    pygame.draw.line(surface, (8, 10, 5), (x+w-inset, y+inset), (x+w-inset, y+h-inset), 1)
    pygame.draw.line(surface, (8, 10, 5), (x+inset, y+h-inset), (x+w-inset, y+h-inset), 1)
    
    # 螺丝钉（四个角）
    screw_offsets = [(4, 4), (w-4, 4), (4, h-4), (w-4, h-4)]
    for ox, oy in screw_offsets:
        draw_screw(surface, x + ox, y + oy)
    
    # 标题（油漆字效果 - 刻印在金属上）
    if title:
        font = pygame.font.SysFont("consolas", 12, bold=True)
        # 阴影（模拟凹陷）
        txt_shadow = font.render(title, True, (30, 32, 25))
        surface.blit(txt_shadow, (x + 14, y + 8))
        # 高光（模拟浮雕）
        txt = font.render(title, True, C_TEXT_LABEL)
        surface.blit(txt, (x + 13, y + 7))

def draw_screw(surface, x, y, size=3):
    """十字槽螺丝钉"""
    pygame.draw.circle(surface, C_METAL_SHADOW, (x, y), size+1)
    pygame.draw.circle(surface, (100, 105, 90), (x, y), size)
    pygame.draw.circle(surface, C_METAL_HIGHLIGHT, (x-1, y-1), size-1)
    # 十字槽
    pygame.draw.line(surface, (50, 55, 42), (x-size+1, y), (x+size-1, y), 1)
    pygame.draw.line(surface, (50, 55, 42), (x, y-size+1), (x, y+size-1), 1)

def draw_crt_display(surface, rect, label=""):
    """绘制内嵌CRT显示器 - 厚重弧形玻璃边框"""
    x, y, w, h = rect
    bezel = 8
    
    # 外框（厚重橡胶/金属混合）
    pygame.draw.rect(surface, C_CRT_BEZEL, (x-bezel, y-bezel, w+bezel*2, h+bezel*2), border_radius=4)
    pygame.draw.rect(surface, C_CRT_BEZEL_HIGHLIGHT, (x-bezel, y-bezel, w+bezel*2, h+bezel*2), width=1, border_radius=4)
    # 内框凹槽
    pygame.draw.rect(surface, C_CRT_BEZEL_SHADOW, (x-2, y-2, w+4, h+4), border_radius=1)
    pygame.draw.rect(surface, C_CRT_GLASS, (x, y, w, h))
    
    # 玻璃反光（顶部弧形）
    glare = pygame.Surface((w, h//5), pygame.SRCALPHA)
    for i in range(h//5):
        alpha = max(0, 12 - i // 2)
        pygame.draw.line(glare, (255, 255, 255, alpha), (0, i), (w, i), 1)
    surface.blit(glare, (x, y))
    
    # 标签（刻在CRT边框下方）
    if label:
        font = pygame.font.SysFont("consolas", 10, bold=True)
        lbl = font.render(label, True, C_TEXT_DIM)
        surface.blit(lbl, (x + w//2 - lbl.get_width()//2, y - bezel - 14))

def draw_crt_effect(surface, rect, scanline_spacing=2, intensity=0.14):
    """CRT磷光屏效果 - 仅屏幕内部"""
    x, y, w, h = rect
    
    # 扫描线
    scan_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for sy in range(0, h, scanline_spacing):
        pygame.draw.line(scan_surf, (0, 0, 0, int(255 * intensity)), (0, sy), (w, sy), 1)
    surface.blit(scan_surf, (x, y))
    
    # 边缘暗角
    vignette = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(min(25, w//4, h//4)):
        alpha = i * 2
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (i, i, w-2*i, h-2*i), 1)
    surface.blit(vignette, (x, y))
    
    # 轻微噪点
    if random.random() < 0.2:
        noise_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for _ in range(max(1, (w * h) // 4000)):
            nx = random.randint(0, w-1)
            ny = random.randint(0, h-1)
            noise_surf.set_at((nx, ny), (255, 255, 255, random.randint(5, 15)))
        surface.blit(noise_surf, (x, y))

def draw_metal_switch(surface, x, y, label_up, label_down, state_up, font):
    """金属拨动开关"""
    # 金属底座
    pygame.draw.rect(surface, C_METAL_SHADOW, (x-14, y-22, 28, 44), border_radius=3)
    pygame.draw.rect(surface, C_METAL_FACE, (x-14, y-22, 28, 44), border_radius=3)
    pygame.draw.line(surface, C_METAL_HIGHLIGHT, (x-13, y+21), (x-13, y-21), 1)
    pygame.draw.line(surface, C_METAL_HIGHLIGHT, (x-13, y-21), (x+12, y-21), 1)
    pygame.draw.line(surface, (30, 34, 24), (x+13, y-21), (x+13, y+21), 1)
    pygame.draw.line(surface, (30, 34, 24), (x-13, y+21), (x+13, y+21), 1)
    
    # 手柄
    handle_y = y - 10 if state_up else y + 10
    pygame.draw.line(surface, (160, 165, 140), (x, y), (x, handle_y), 3)
    pygame.draw.circle(surface, (200, 205, 180), (x, handle_y), 4)
    pygame.draw.circle(surface, C_METAL_HIGHLIGHT, (x-1, handle_y-1), 2)
    
    # 刻字标签
    lbl_u = font.render(label_up, True, C_PHOSPHOR_GREEN if state_up else C_TEXT_DIM)
    lbl_d = font.render(label_down, True, C_PHOSPHOR_RED if not state_up else C_TEXT_DIM)
    surface.blit(lbl_u, (x - lbl_u.get_width()//2, y - 36))
    surface.blit(lbl_d, (x - lbl_d.get_width()//2, y + 26))

def draw_illuminated_lamp(surface, x, y, label, color_on, is_lit, font):
    """物理指示灯（灯泡在金属灯座中）"""
    # 金属灯座
    pygame.draw.circle(surface, C_METAL_SHADOW, (x, y), 13)
    pygame.draw.circle(surface, C_METAL_FACE, (x, y), 12)
    pygame.draw.circle(surface, C_METAL_HIGHLIGHT, (x-1, y-1), 11, 1)
    
    # 灯泡
    color = color_on if is_lit else C_LAMP_OFF
    pygame.draw.circle(surface, color, (x, y), 8)
    
    if is_lit:
        glow = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color[:3], 50), (18, 18), 15)
        surface.blit(glow, (x-18, y-18), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surface, (255, 255, 255), (x-2, y-2), 2)
    
    lines = label.split("\n")
    for i, line in enumerate(lines):
        lbl = font.render(line, True, C_TEXT_MAIN if is_lit else C_TEXT_DIM)
        surface.blit(lbl, (x - lbl.get_width()//2, y + 16 + i*13))

def draw_metal_button(surface, x, y, label, is_active, font, radius=22):
    """金属发射按钮 - 大圆形，红色玻璃罩"""
    # 金属底座
    pygame.draw.circle(surface, C_METAL_SHADOW, (x, y), radius+5)
    pygame.draw.circle(surface, C_METAL_FACE, (x, y), radius+4)
    pygame.draw.circle(surface, C_METAL_HIGHLIGHT, (x-1, y-1), radius+3, 1)
    
    # 按钮本体（红色玻璃/油漆）
    color = C_PHOSPHOR_RED if is_active else C_PHOSPHOR_RED_DIM
    pygame.draw.circle(surface, color, (x, y), radius)
    pygame.draw.circle(surface, (255, 130, 120) if is_active else C_METAL_SHADOW, (x, y), radius, 2)
    
    if is_active:
        pygame.draw.circle(surface, (255, 160, 150), (x-4, y-4), 4)
        # 发光外圈
        glow = pygame.Surface((radius*3, radius*3), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 60, 40, 40), (radius*3//2, radius*3//2), radius+8)
        surface.blit(glow, (x-radius*3//2, y-radius*3//2), special_flags=pygame.BLEND_ADD)
    
    lbl = font.render(label, True, C_TEXT_MAIN)
    surface.blit(lbl, (x - lbl.get_width()//2, y - lbl.get_height()//2))

def draw_dial_gauge(surface, cx, cy, radius, value, max_val, label, font):
    """金属边框圆形仪表"""
    # 金属外框
    pygame.draw.circle(surface, C_METAL_SHADOW, (cx, cy), radius+7)
    pygame.draw.circle(surface, C_METAL_FACE, (cx, cy), radius+6)
    pygame.draw.circle(surface, C_METAL_HIGHLIGHT, (cx-1, cy-1), radius+5, 1)
    # 表盘（深色）
    pygame.draw.circle(surface, C_RECESS, (cx, cy), radius)
    pygame.draw.circle(surface, C_RECESS_BORDER, (cx, cy), radius, 1)
    
    for i in range(11):
        angle = math.radians(225 - i * 27)
        x1 = cx + (radius-6) * math.cos(angle)
        y1 = cy - (radius-6) * math.sin(angle)
        x2 = cx + (radius-12) * math.cos(angle)
        y2 = cy - (radius-12) * math.sin(angle)
        pygame.draw.line(surface, C_TEXT_DIM, (x1, y1), (x2, y2), 2 if i%5==0 else 1)
    
    pct = clamp(value / max_val, 0, 1)
    ptr_angle = math.radians(225 - pct * 270)
    px = cx + (radius-18) * math.cos(ptr_angle)
    py = cy - (radius-18) * math.sin(ptr_angle)
    pygame.draw.line(surface, C_PHOSPHOR_GREEN, (cx, cy), (px, py), 2)
    pygame.draw.circle(surface, C_METAL_FACE, (cx, cy), 4)
    
    lbl = font.render(label, True, C_TEXT_DIM)
    surface.blit(lbl, (cx - lbl.get_width()//2, cy + 14))
    
    val_txt = font.render(f"{int(value)}", True, C_TEXT_MAIN)
    surface.blit(val_txt, (cx - val_txt.get_width()//2, cy + 28))

def draw_chassis_background(surface, width, height):
    """绘制机箱外壳背景纹理"""
    surface.fill(C_CHASSIS)
    # 细微纹理线（模拟金属表面划痕）
    for _ in range(30):
        lx = random.randint(0, width)
        ly = random.randint(0, height)
        ll = random.randint(20, 100)
        pygame.draw.line(surface, C_CHASSIS_TEXTURE, (lx, ly), (lx+ll, ly), 1)

# ==========================================
# 实体类
# ==========================================

class Target:
    def __init__(self, scenario_type):
        self.type = scenario_type
        self.active = True
        self.hit = False
        self.crashed = False
        self.history = []
        self.smoke_particles = []
        self.last_history_time = 0
        
        dist = random.randint(40000, 60000)
        angle = random.uniform(0, 360)
        
        rad = math.radians(angle)
        self.x = dist * math.sin(rad)
        self.y = -dist * math.cos(rad)
        
        if self.type == SCENARIO_DRONE:
            self.z = random.randint(3000, 6000)
            self.speed = 250
            self.name = "MQM-107 STREAKER"
            self.rcs = 1.0
            self.desc = "SUBSONIC TARGET DRONE"
            self.max_g = 3.0
        elif self.type == SCENARIO_F4E:
            self.z = random.randint(500, 8000)
            self.speed = random.randint(350, 550)
            self.name = "F-4E PHANTOM II"
            self.rcs = 6.0
            self.desc = "MULTI-ROLE FIGHTER"
            self.max_g = 7.5
        elif self.type == SCENARIO_F117:
            self.z = random.randint(3000, 5000)
            self.speed = 280
            self.name = "F-117A NIGHTHAWK"
            self.rcs = 0.025
            self.desc = "STEALTH ATTACK AIRCRAFT"
            self.max_g = 6.0
        
        math_angle = math.atan2(-self.y, self.x)
        offset = random.uniform(-0.3, 0.3)
        heading = math_angle + offset + math.pi
        
        self.vx = self.speed * math.cos(heading)
        self.vy = -self.speed * math.sin(heading)
        self.vz = 0
        self.heading = heading

    def update(self, dt, current_time):
        if self.crashed:
            return
        
        if current_time - self.last_history_time > 500:
            self.history.append((self.x, self.y))
            self.last_history_time = current_time
            if len(self.history) > 200:
                self.history.pop(0)
        
        if self.hit:
            self.vz -= 15 * dt
            self.vx *= 0.98
            self.vy *= 0.98
            
            if random.random() < 0.6:
                self.smoke_particles.append({
                    'x': self.x + random.uniform(-20, 20),
                    'y': self.y + random.uniform(-20, 20),
                    'z': self.z + random.uniform(-10, 10),
                    'alpha': 1.0,
                    'size': random.uniform(1.0, 3.0)
                })
        
        for p in self.smoke_particles:
            p['alpha'] -= dt * 0.3
            p['z'] += random.uniform(5, 15) * dt
            p['x'] += random.uniform(-5, 5) * dt
            p['y'] += random.uniform(-5, 5) * dt
        self.smoke_particles = [p for p in self.smoke_particles if p['alpha'] > 0]
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        
        if self.z <= 0:
            self.z = 0
            self.crashed = True
            self.vx = self.vy = self.vz = 0
        
        if math.sqrt(self.x**2 + self.y**2) > 100000:
            self.active = False

    def get_polar(self):
        ground_dist = math.sqrt(self.x**2 + self.y**2)
        slant_dist = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        az = math.degrees(math.atan2(self.x, -self.y))
        az = normalize_angle(az)
        el = math.degrees(math.atan2(self.z, ground_dist)) if ground_dist > 0 else 90
        return slant_dist, az, el

    def get_radial_velocity(self):
        dist = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if dist < 1:
            return 0
        ux, uy, uz = self.x/dist, self.y/dist, self.z/dist
        radial_v = -(self.vx * ux + self.vy * uy + self.vz * uz)
        return radial_v


class Missile:
    def __init__(self):
        self.active = False
        self.x = self.y = self.z = 0
        self.vx = self.vy = self.vz = 0
        self.speed = 0
        
        self.max_speed = 780
        self.boost_time = 4.0
        self.sustain_time = 22.0
        self.total_fuel = self.boost_time + self.sustain_time
        self.fuel = self.total_fuel
        self.max_g = 6.0
        self.prox_fuse_range = 50
        
        self.detonated = False
        self.target_ref = None
        self.guidance_method = GUIDANCE_LEAD
        self.trail = []
        self.history = []
        self.launch_time = 0
        self.last_history_time = 0

    def launch(self, target, guidance_method, current_time):
        self.active = True
        self.x = self.y = 0
        self.z = 20
        self.speed = 100
        self.vx = self.vy = 0
        self.vz = self.speed * 0.8
        self.fuel = self.total_fuel
        self.detonated = False
        self.target_ref = target
        self.guidance_method = guidance_method
        self.trail = []
        self.history = []
        self.launch_time = current_time

    def update(self, dt, current_time, radar_tracking):
        if not self.active:
            return False
        
        if current_time - self.last_history_time > 100:
            self.history.append((self.x, self.y))
            self.last_history_time = current_time
        
        self.trail.append((self.x, self.y, self.z))
        if len(self.trail) > 50:
            self.trail.pop(0)
        
        self.fuel -= dt
        
        if self.fuel > self.sustain_time:
            if self.speed < self.max_speed:
                self.speed += 200 * dt
        elif self.fuel > 0:
            if self.speed < self.max_speed:
                self.speed += 50 * dt
        else:
            self.speed *= 0.995
            if self.speed < 100:
                self.active = False
                return False
        
        guided = False
        tx, ty, tz = 0, 0, 0
        
        if radar_tracking and self.target_ref and self.target_ref.active and not self.target_ref.crashed:
            dist_to_target = math.sqrt(
                (self.target_ref.x - self.x)**2 +
                (self.target_ref.y - self.y)**2 +
                (self.target_ref.z - self.z)**2
            )
            
            if self.guidance_method == GUIDANCE_LEAD:
                time_to_impact = dist_to_target / self.max_speed
                tx = self.target_ref.x + self.target_ref.vx * time_to_impact * 0.8
                ty = self.target_ref.y + self.target_ref.vy * time_to_impact * 0.8
                tz = self.target_ref.z + self.target_ref.vz * time_to_impact * 0.8
            else:
                tx, ty, tz = self.target_ref.x, self.target_ref.y, self.target_ref.z
            
            guided = True
            
            if dist_to_target < self.prox_fuse_range and not self.detonated:
                self.detonated = True
                self.active = False
                return True
        
        if guided:
            dx = tx - self.x
            dy = ty - self.y
            dz = tz - self.z
            d_total = math.sqrt(dx**2 + dy**2 + dz**2)
            
            if d_total > 0:
                desired_vx = (dx / d_total) * self.speed
                desired_vy = (dy / d_total) * self.speed
                desired_vz = (dz / d_total) * self.speed
                
                max_turn = self.max_g * 9.8 * dt / self.speed
                
                def limit_turn(current, desired, max_delta):
                    delta = desired - current
                    if abs(delta) > max_delta * self.speed:
                        delta = max_delta * self.speed * (1 if delta > 0 else -1)
                    return current + delta
                
                self.vx = limit_turn(self.vx, desired_vx, max_turn)
                self.vy = limit_turn(self.vy, desired_vy, max_turn)
                self.vz = limit_turn(self.vz, desired_vz, max_turn)
        else:
            self.vz -= 9.8 * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        
        if self.z < 0:
            self.active = False
        
        return False

    def get_polar(self):
        ground_dist = math.sqrt(self.x**2 + self.y**2)
        slant_dist = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        az = math.degrees(math.atan2(self.x, -self.y))
        az = normalize_angle(az)
        el = math.degrees(math.atan2(self.z, ground_dist)) if ground_dist > 0 else 90
        return slant_dist, az, el


class LauncherGroup:
    def __init__(self):
        self.launchers = [
            {'azimuth': 0, 'missiles': 2, 'ready': False, 'prep_timer': 0},
            {'azimuth': 90, 'missiles': 2, 'ready': False, 'prep_timer': 0},
            {'azimuth': 180, 'missiles': 2, 'ready': False, 'prep_timer': 0},
            {'azimuth': 270, 'missiles': 2, 'ready': False, 'prep_timer': 0},
        ]
        self.selected = 0
        self.prep_time = 30.0

    def update(self, dt, power_on):
        if not power_on:
            for l in self.launchers:
                l['ready'] = False
                l['prep_timer'] = 0
            return
        
        for l in self.launchers:
            if l['prep_timer'] > 0:
                l['prep_timer'] -= dt
                if l['prep_timer'] <= 0:
                    l['prep_timer'] = 0
                    if l['missiles'] > 0:
                        l['ready'] = True

    def start_prep(self, index):
        if 0 <= index < 4:
            l = self.launchers[index]
            if l['missiles'] > 0 and not l['ready']:
                l['prep_timer'] = self.prep_time

    def can_fire(self, index, radar_az):
        if index < 0 or index >= 4:
            return False, "INVALID"
        
        l = self.launchers[index]
        
        if l['missiles'] <= 0:
            return False, "EMPTY"
        
        if not l['ready']:
            return False, "NOT READY"
        
        az_diff = abs(get_angle_diff(l['azimuth'], radar_az))
        if az_diff < 30:
            return False, "BLOCKED"
        
        return True, "OK"

    def fire(self, index):
        if 0 <= index < 4:
            l = self.launchers[index]
            if l['missiles'] > 0:
                l['missiles'] -= 1
                if l['missiles'] <= 0:
                    l['ready'] = False
                return True
        return False

    def get_total_missiles(self):
        return sum(l['missiles'] for l in self.launchers)


# ==========================================
# 主模拟器类
# ==========================================

class SA3Simulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("S-125 NEVA // SA-3 GOA SAM SIMULATOR")
        self.clock = pygame.time.Clock()
        
        self.font_sm = pygame.font.SysFont("consolas", 11)
        self.font = pygame.font.SysFont("consolas", 13)
        self.font_md = pygame.font.SysFont("consolas", 15, bold=True)
        self.font_lg = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_ru = pygame.font.SysFont("consolas", 12, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 44, bold=True)
        self.font_title_sm = pygame.font.SysFont("consolas", 26, bold=True)
        
        self.reset_game()

    def reset_game(self):
        self.state = STATE_MENU
        self.scenario = SCENARIO_DRONE
        self.log = []
        
        self.sw_grid = False
        self.sw_sys = False
        self.sw_hv = False
        self.sw_ant = False
        
        self.sw_range_mode = 0
        self.sw_sdc = False
        
        self.sw_guidance = GUIDANCE_LEAD
        self.sw_salvo = 1
        self.sw_auto = False
        
        self.sw_tv_fov = 0
        
        self.p18_angle = 0.0
        self.ant_az = 180.0
        self.ant_el = 10.0
        self.range_gate = 30000.0
        self.scan_angle = 0.0
        self.scanning = True
        
        self.locked = False
        self.track_quality = 0.0
        
        self.launchers = LauncherGroup()
        self.active_missiles = []
        
        self.target = Target(SCENARIO_DRONE)
        self.target.active = False
        
        self.report = {
            "result": "PENDING",
            "lock_range": 0,
            "hit_range": 0,
            "missiles_fired": 0
        }
        
        self.plot_open = False
        
        self.add_log("SYSTEM RESET")

    @property
    def pwr_grid(self):
        return self.sw_grid
    
    @property
    def pwr_sys(self):
        return self.sw_grid and self.sw_sys
    
    @property
    def pwr_hv(self):
        return self.pwr_sys and self.sw_hv
    
    @property
    def pwr_ant(self):
        return self.pwr_sys and self.sw_ant
    
    @property
    def max_range(self):
        return 40000 if self.sw_range_mode == 1 else 80000

    def add_log(self, msg):
        self.log.append(msg)
        if len(self.log) > 6:
            self.log.pop(0)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            current_time = pygame.time.get_ticks()
            self.handle_input(dt)
            self.update(dt, current_time)
            self.draw()

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        
        if self.state == STATE_SIMULATION:
            if self.pwr_ant:
                spd = 25 * dt
                if keys[pygame.K_LSHIFT]:
                    spd *= 0.2
                if keys[pygame.K_LEFT]:
                    self.ant_az = normalize_angle(self.ant_az - spd)
                if keys[pygame.K_RIGHT]:
                    self.ant_az = normalize_angle(self.ant_az + spd)
                if keys[pygame.K_UP]:
                    self.ant_el = clamp(self.ant_el + spd, 0, 85)
                if keys[pygame.K_DOWN]:
                    self.ant_el = clamp(self.ant_el - spd, 0, 85)
            
            if self.pwr_sys:
                gate_spd = 15000 * dt
                if keys[pygame.K_LSHIFT]:
                    gate_spd *= 0.1
                if keys[pygame.K_w]:
                    self.range_gate = min(self.max_range - 1000, self.range_gate + gate_spd)
                if keys[pygame.K_s]:
                    self.range_gate = max(2000, self.range_gate - gate_spd)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_click(event.pos)

            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key == pygame.K_1:
                        self.state = STATE_BRIEFING
                    if event.key == pygame.K_2:
                        self.state = STATE_MANUAL
                    if event.key == pygame.K_3:
                        pygame.quit()
                        sys.exit()
                
                elif self.state == STATE_BRIEFING:
                    if event.key == pygame.K_1:
                        self.setup_scenario(SCENARIO_DRONE)
                        self.state = STATE_SIMULATION
                    if event.key == pygame.K_2:
                        self.setup_scenario(SCENARIO_F4E)
                        self.state = STATE_SIMULATION
                    if event.key == pygame.K_3:
                        self.setup_scenario(SCENARIO_F117)
                        self.state = STATE_SIMULATION
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_MENU
                
                elif self.state == STATE_MANUAL:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_MENU
                
                elif self.state == STATE_SIMULATION:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_DEBRIEFING
                    
                    if event.key == pygame.K_1:
                        self.sw_grid = not self.sw_grid
                        self.add_log("GRID " + ("ON" if self.sw_grid else "OFF"))
                    if event.key == pygame.K_2:
                        self.sw_sys = not self.sw_sys
                        self.add_log("SYS " + ("ON" if self.sw_sys else "OFF"))
                    if event.key == pygame.K_3:
                        self.sw_hv = not self.sw_hv
                        self.add_log("HIGH VOLT " + ("ON" if self.sw_hv else "OFF"))
                    if event.key == pygame.K_4:
                        self.sw_ant = not self.sw_ant
                        self.add_log("DRIVE " + ("ON" if self.sw_ant else "OFF"))
                    
                    if event.key == pygame.K_r:
                        self.sw_range_mode = 1 - self.sw_range_mode
                        self.add_log(f"RANGE {40 if self.sw_range_mode else 80}KM")
                    if event.key == pygame.K_m:
                        self.sw_sdc = not self.sw_sdc
                        self.add_log("MTI " + ("ON" if self.sw_sdc else "OFF"))
                    
                    if event.key == pygame.K_g:
                        self.sw_guidance = 1 - self.sw_guidance
                        method = "TT (3-Point)" if self.sw_guidance else "PS (Lead)"
                        self.add_log(f"METHOD: {method}")
                    
                    if event.key == pygame.K_F1:
                        self.launchers.start_prep(0)
                    if event.key == pygame.K_F2:
                        self.launchers.start_prep(1)
                    if event.key == pygame.K_F3:
                        self.launchers.start_prep(2)
                    if event.key == pygame.K_F4:
                        self.launchers.start_prep(3)
                    
                    if event.key == pygame.K_TAB:
                        self.launchers.selected = (self.launchers.selected + 1) % 4
                        self.add_log(f"LNCHR {self.launchers.selected + 1}")
                    
                    if event.key == pygame.K_z:
                        self.sw_salvo = 2 if self.sw_salvo == 1 else 1
                        self.add_log("SALVO" if self.sw_salvo == 2 else "SINGLE")
                    
                    if event.key == pygame.K_a:
                        self.sw_auto = not self.sw_auto
                        self.add_log("AUTO " + ("ON" if self.sw_auto else "OFF"))
                    
                    if event.key == pygame.K_t:
                        self.sw_tv_fov = 1 - self.sw_tv_fov
                    
                    if event.key == pygame.K_SPACE:
                        self.fire_missile()
                    
                    if event.key == pygame.K_p:
                        self.plot_open = not self.plot_open
                
                elif self.state == STATE_DEBRIEFING:
                    if event.key == pygame.K_ESCAPE:
                        self.reset_game()

    def handle_mouse_click(self, pos):
        mx, my = pos
        
        if self.state == STATE_MENU:
            cx = SCREEN_WIDTH // 2
            start_y = 380
            for i in range(3):
                rect = pygame.Rect(cx - 220, start_y + i * 85, 440, 65)
                if rect.collidepoint(mx, my):
                    if i == 0: self.state = STATE_BRIEFING
                    elif i == 1: self.state = STATE_MANUAL
                    elif i == 2: pygame.quit(); sys.exit()

        elif self.state == STATE_BRIEFING:
            doc_w, doc_h = 920, 740
            doc_x = (SCREEN_WIDTH - doc_w) // 2
            doc_y = (SCREEN_HEIGHT - doc_h) // 2
            y_offset = doc_y + 110
            
            for i in range(3):
                rect = pygame.Rect(doc_x + 40, y_offset + i * 175, doc_w - 80, 155)
                if rect.collidepoint(mx, my):
                    if i == 0: self.setup_scenario(SCENARIO_DRONE)
                    elif i == 1: self.setup_scenario(SCENARIO_F4E)
                    elif i == 2: self.setup_scenario(SCENARIO_F117)
                    self.state = STATE_SIMULATION
            
            if my > doc_y + doc_h - 60:
                self.state = STATE_MENU

        elif self.state == STATE_MANUAL:
            self.state = STATE_MENU

        elif self.state == STATE_DEBRIEFING:
            if my > 750:
                self.reset_game()

        elif self.state == STATE_SIMULATION:
            if self.plot_open:
                board_w, board_h = 720, 720
                board_x = (SCREEN_WIDTH - board_w) // 2
                board_y = (SCREEN_HEIGHT - board_h) // 2
                if board_y + board_h - 50 < my < board_y + board_h:
                    self.plot_open = False
                return

            px, py = 10, 440
            sw_y = py + 70
            sw_spacing = 70
            for i in range(4):
                sw_x = px + 40 + i * sw_spacing
                rect = pygame.Rect(sw_x - 20, sw_y - 30, 40, 60)
                if rect.collidepoint(mx, my):
                    if i == 0: 
                        self.sw_grid = not self.sw_grid
                        self.add_log("GRID " + ("ON" if self.sw_grid else "OFF"))
                    elif i == 1: 
                        self.sw_sys = not self.sw_sys
                        self.add_log("SYS " + ("ON" if self.sw_sys else "OFF"))
                    elif i == 2: 
                        self.sw_hv = not self.sw_hv
                        self.add_log("HIGH VOLT " + ("ON" if self.sw_hv else "OFF"))
                    elif i == 3: 
                        self.sw_ant = not self.sw_ant
                        self.add_log("DRIVE " + ("ON" if self.sw_ant else "OFF"))
            
            if pygame.Rect(px + 10, py + 450 - 40, 200, 30).collidepoint(mx, my):
                self.plot_open = True

            rx, ry = 320, 10
            sw_y = ry + 420 + 55
            sw_start = rx + 560
            if pygame.Rect(sw_start - 20, sw_y - 30, 40, 60).collidepoint(mx, my):
                self.sw_range_mode = 1 - self.sw_range_mode
                self.add_log(f"RANGE {40 if self.sw_range_mode else 80}KM")
            if pygame.Rect(sw_start + 60 - 20, sw_y - 30, 40, 60).collidepoint(mx, my):
                self.sw_sdc = not self.sw_sdc
                self.add_log("MTI " + ("ON" if self.sw_sdc else "OFF"))
            if pygame.Rect(sw_start + 120 - 20, sw_y - 30, 40, 60).collidepoint(mx, my):
                self.sw_guidance = 1 - self.sw_guidance
                method = "TT (3-Point)" if self.sw_guidance else "PS (Lead)"
                self.add_log(f"METHOD: {method}")
            if pygame.Rect(sw_start + 180 - 20, sw_y - 30, 40, 60).collidepoint(mx, my):
                self.sw_tv_fov = 1 - self.sw_tv_fov

            lx, ly = 1280, 10
            lw = 310
            
            grid_x = lx + 45
            grid_y = ly + 40
            cell_w = 58
            cell_h = 25
            
            for col in range(4):
                col_x = grid_x + col * cell_w
                if pygame.Rect(col_x, grid_y, cell_w, cell_h * 2 + 25).collidepoint(mx, my):
                    self.launchers.selected = col
                    self.add_log(f"LNCHR {col + 1}")
                
                rdy_y = grid_y + 25 + cell_h
                if pygame.Rect(col_x, rdy_y, cell_w, cell_h).collidepoint(mx, my):
                    self.launchers.start_prep(col)

            sw_y = ly + 220
            center_x = lx + lw // 2
            if pygame.Rect(center_x - 90 - 20, sw_y - 30, 40, 60).collidepoint(mx, my):
                self.sw_salvo = 2 if self.sw_salvo == 1 else 1
                self.add_log("SALVO" if self.sw_salvo == 2 else "SINGLE")
            if pygame.Rect(center_x - 20, sw_y - 30, 40, 60).collidepoint(mx, my):
                self.sw_auto = not self.sw_auto
                self.add_log("AUTO " + ("ON" if self.sw_auto else "OFF"))
            if pygame.Rect(center_x + 90 - 20, sw_y - 30, 40, 60).collidepoint(mx, my):
                self.sw_hv = not self.sw_hv
                self.add_log("HIGH VOLT " + ("ON" if self.sw_hv else "OFF"))

            fire_x, fire_y = lx + lw // 2, ly + 470
            if (mx - fire_x)**2 + (my - fire_y)**2 <= 35**2:
                self.fire_missile()

    def setup_scenario(self, scenario):
        self.scenario = scenario
        self.target = Target(scenario)
        self.target.active = True
        self.add_log(f"TARGET: {self.target.name}")

    def update(self, dt, current_time):
        if self.state == STATE_MENU:
            self.p18_angle = (self.p18_angle + 30 * dt) % 360
            return
        
        if self.state != STATE_SIMULATION:
            return
        
        self.target.update(dt, current_time)
        
        if self.pwr_grid:
            self.p18_angle = (self.p18_angle + 50 * dt) % 360
        
        if self.scanning and self.pwr_hv:
            self.scan_angle += 60 * dt
            if self.scan_angle > 5:
                self.scan_angle = -5
        
        self.launchers.update(dt, self.pwr_sys)
        
        self.update_tracking(dt)
        
        for m in self.active_missiles:
            hit = m.update(dt, current_time, self.locked and self.pwr_hv)
            if hit:
                self.target.hit = True
                self.report["hit_range"] = int(self.target.get_polar()[0])
                self.report["result"] = "TARGET DESTROYED"
                self.add_log("SPLASH!")
        
        self.active_missiles = [m for m in self.active_missiles if m.active]
        
        if (self.sw_auto and self.locked and self.pwr_hv and
            self.target.active and not self.target.crashed and not self.target.hit and
            len(self.active_missiles) == 0):
            if self.check_launch_envelope():
                self.fire_missile()
        
        if self.target.crashed and self.report["result"] == "PENDING":
            if self.target.hit:
                self.report["result"] = "TARGET DESTROYED"
            else:
                self.report["result"] = "TARGET LOST"
        
        if not self.target.active and self.report["result"] == "PENDING":
            self.report["result"] = "TARGET ESCAPED"
            self.state = STATE_DEBRIEFING

    def update_tracking(self, dt):
        if not (self.pwr_hv and self.pwr_ant):
            self.locked = False
            self.track_quality = 0
            self.scanning = True
            return
        
        if not self.target.active or self.target.crashed:
            self.locked = False
            self.track_quality = max(0, self.track_quality - dt * 2)
            return
        
        d, az, el = self.target.get_polar()
        
        az_diff = abs(get_angle_diff(az, self.ant_az))
        el_diff = abs(el - self.ant_el)
        
        az_beam = 4.0
        el_beam = 5.0 if self.scanning else 2.0
        
        in_beam = az_diff < az_beam and el_diff < el_beam
        in_gate = abs(d - self.range_gate) < 1500
        
        detect_prob = min(1.0, self.target.rcs * 0.5) if self.target.rcs < 1.0 else 1.0
        
        if in_beam and in_gate and random.random() < detect_prob:
            self.track_quality = min(1.0, self.track_quality + dt * 1.5)
            
            if self.track_quality >= 0.7:
                if not self.locked:
                    self.locked = True
                    self.scanning = False
                    self.report["lock_range"] = int(d)
                    self.add_log("LOCKED!")
                
                track_rate = 3.0 * dt
                self.ant_az += get_angle_diff(az, self.ant_az) * track_rate
                self.ant_el += (el - self.ant_el) * track_rate
                self.range_gate += (d - self.range_gate) * track_rate
        else:
            self.track_quality = max(0, self.track_quality - dt * 1.0)
            if self.track_quality < 0.3 and self.locked:
                self.locked = False
                self.scanning = True
                self.add_log("LOCK LOST")

    def check_launch_envelope(self):
        if not self.target.active:
            return False
        
        d, _, el = self.target.get_polar()
        h = self.target.z
        
        if d < 3500 or d > 25000:
            return False
        
        if h < 20 or h > 18000:
            return False
        
        return True

    def fire_missile(self):
        if not self.pwr_sys:
            self.add_log("SYS OFF")
            return
        
        if not self.pwr_hv:
            self.add_log("HV OFF")
            return
        
        if not self.locked:
            self.add_log("NO LOCK")
            return
        
        idx = self.launchers.selected
        can_fire, reason = self.launchers.can_fire(idx, self.ant_az)
        
        if not can_fire:
            self.add_log(f"DENIED: {reason}")
            return
        
        count = min(self.sw_salvo, self.launchers.launchers[idx]['missiles'])
        current_time = pygame.time.get_ticks()
        
        for i in range(count):
            if self.launchers.fire(idx):
                m = Missile()
                m.launch(self.target, self.sw_guidance, current_time + i * 5000)
                self.active_missiles.append(m)
                self.report["missiles_fired"] += 1
        
        self.add_log("LAUNCH!")


    # ==========================================
    # 绘制函数
    # ==========================================

    def draw(self):
        draw_chassis_background(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if self.state == STATE_SIMULATION:
            self.draw_cockpit()
            if self.plot_open:
                self.draw_plotting_board()
        elif self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_BRIEFING:
            self.draw_briefing()
        elif self.state == STATE_DEBRIEFING:
            self.draw_debriefing()
        elif self.state == STATE_MANUAL:
            self.draw_manual()
        
        pygame.display.flip()

    def draw_cockpit(self):
        self.draw_panel_p18(10, 10, 300, 440)
        self.draw_panel_fcr(320, 10, 950, 570)
        self.draw_panel_launch(1280, 10, 310, 570)
        self.draw_panel_controls(10, 460, 300, 430)
        self.draw_panel_status(320, 590, 950, 300)

    def draw_panel_p18(self, x, y, w, h):
        """P-18预警雷达面板 - 金属外壳包裹圆形CRT"""
        draw_metal_panel(self.screen, (x, y, w, h), "P-18 ACQUISITION RADAR")
        
        cx, cy = x + w//2, y + h//2 + 10
        radius = 125
        
        # CRT显示器厚重边框
        draw_crt_display(self.screen, (cx-radius, cy-radius, radius*2, radius*2), "PPI SCOPE")
        
        pygame.draw.circle(self.screen, C_P18_BG, (cx, cy), radius)
        pygame.draw.circle(self.screen, C_PHOSPHOR_AMBER_DIM, (cx, cy), radius, 2)
        
        if self.pwr_grid:
            scale = radius / 80000.0
            
            for i in range(1, 5):
                r = i * (radius // 4)
                pygame.draw.circle(self.screen, C_P18_GRID, (cx, cy), r, 1)
            
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                x1 = cx + radius * 0.9 * math.sin(rad)
                y1 = cy - radius * 0.9 * math.cos(rad)
                pygame.draw.line(self.screen, C_P18_GRID, (cx, cy), (x1, y1), 1)
            
            # 扫描线
            rad = math.radians(self.p18_angle)
            ex = cx + radius * math.sin(rad)
            ey = cy - radius * math.cos(rad)
            pygame.draw.line(self.screen, C_P18_SWEEP, (cx, cy), (ex, ey), 2)
            
            # 目标回波
            if self.target.active and not self.target.crashed:
                td, taz, _ = self.target.get_polar()
                if td < 80000:
                    angle_diff = abs(get_angle_diff(self.p18_angle, taz))
                    if angle_diff < 8:
                        trad = math.radians(taz)
                        tx = cx + td * scale * math.sin(trad)
                        ty = cy - td * scale * math.cos(trad)
                        
                        intensity = 1.0 - angle_diff / 8.0
                        size = int(2 + self.target.rcs * intensity)
                        
                        glow = pygame.Surface((size*6, size*6), pygame.SRCALPHA)
                        pygame.draw.circle(glow, (*C_P18_BLIP[:3], int(100*intensity)), (size*3, size*3), size*3)
                        self.screen.blit(glow, (int(tx)-size*3, int(ty)-size*3), special_flags=pygame.BLEND_ADD)
                        pygame.draw.circle(self.screen, C_P18_BLIP, (int(tx), int(ty)), size)
            
            # 导弹回波
            for m in self.active_missiles:
                md, maz, _ = m.get_polar()
                if md < 80000:
                    angle_diff = abs(get_angle_diff(self.p18_angle, maz))
                    if angle_diff < 8:
                        mrad = math.radians(maz)
                        mx = cx + md * scale * math.sin(mrad)
                        my = cy - md * scale * math.cos(mrad)
                        pygame.draw.circle(self.screen, C_P18_MISSILE, (int(mx), int(my)), 2)
        
        # 距离标尺
        for i, km in enumerate([20, 40, 60, 80]):
            txt = self.font_sm.render(str(km), True, C_P18_AFTERGLOW)
            r = i * (radius // 4) + radius // 4
            self.screen.blit(txt, (cx + 4, cy - r - 6))
        
        draw_crt_effect(self.screen, (cx-radius, cy-radius, radius*2, radius*2), scanline_spacing=2, intensity=0.15)

    def draw_panel_fcr(self, x, y, w, h):
        """火控雷达主面板 - 金属外壳包裹多个CRT"""
        draw_metal_panel(self.screen, (x, y, w, h), "SNR-125M1 FIRE CONTROL")
        
        # TV光学显示器
        self.draw_tv_display(x + 350, y + 40, 330, 260)
        
        # И1显示器
        self.draw_scope_i1(x + 20, y + 40, 175, 340)
        
        # И2显示器
        self.draw_scope_i2(x + 740, y + 40, 175, 340)
        
        # 仪表行
        gauge_y = y + 400
        
        draw_dial_gauge(self.screen, x + 90, gauge_y + 50, 40, self.ant_el, 90, "ELEV", self.font_sm)
        draw_dial_gauge(self.screen, x + 195, gauge_y + 50, 40, self.range_gate/1000, self.max_range/1000, "RNG km", self.font_sm)
        
        radial_v = self.target.get_radial_velocity() if self.target.active else 0
        draw_dial_gauge(self.screen, x + 300, gauge_y + 50, 40, max(0, radial_v), 700, "Vr m/s", self.font_sm)
        
        draw_dial_gauge(self.screen, x + 405, gauge_y + 50, 40, self.track_quality * 100, 100, "QUAL %", self.font_sm)
        
        # 开关行
        sw_y = gauge_y + 55
        sw_start = x + 500
        
        draw_metal_switch(self.screen, sw_start, sw_y, "80", "40", self.sw_range_mode == 0, self.font_sm)
        draw_metal_switch(self.screen, sw_start + 60, sw_y, "MTI", "---", self.sw_sdc, self.font_sm)
        draw_metal_switch(self.screen, sw_start + 120, sw_y, "PS", "TT", self.sw_guidance == GUIDANCE_LEAD, self.font_sm)
        draw_metal_switch(self.screen, sw_start + 180, sw_y, "WIDE", "NAR", self.sw_tv_fov == 0, self.font_sm)
        
        # 指示灯
        lamp_y = gauge_y + 55
        lamp_start = x + 720
        
        draw_illuminated_lamp(self.screen, lamp_start, lamp_y, "LOCK", C_LAMP_GREEN, self.locked, self.font_sm)
        draw_illuminated_lamp(self.screen, lamp_start + 50, lamp_y, "TRK", C_LAMP_GREEN, self.track_quality > 0.5, self.font_sm)
        draw_illuminated_lamp(self.screen, lamp_start + 100, lamp_y, "AUTO", C_LAMP_GREEN, self.locked and self.pwr_hv, self.font_sm)
        draw_illuminated_lamp(self.screen, lamp_start + 150, lamp_y, "AUTH", C_LAMP_YELLOW, self.check_launch_envelope() and self.locked, self.font_sm)

    def draw_scope_i1(self, x, y, w, h):
        """И1显示器 - 精细跟踪 CRT"""
        draw_crt_display(self.screen, (x, y, w, h), "I1 PRECISION")
        pygame.draw.rect(self.screen, C_FCR_BG, (x, y, w, h))
        
        if not self.pwr_sys:
            noise = pygame.Surface((w, h), pygame.SRCALPHA)
            for _ in range(50):
                nx = random.randint(0, w-1)
                ny = random.randint(0, h-1)
                noise.set_at((nx, ny), (20, 50, 30, random.randint(10, 40)))
            self.screen.blit(noise, (x, y))
            draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.2)
            return
        
        cx = x + w // 2
        cy = y + h // 2
        
        pygame.draw.line(self.screen, C_FCR_GRID, (cx, y), (cx, y+h), 1)
        pygame.draw.line(self.screen, C_FCR_STROBE, (x, cy), (x+w, cy), 2)
        
        for offset in [-1000, 1000]:
            py = cy - (offset / 1500) * (h/2)
            pygame.draw.line(self.screen, C_FCR_GRID, (x, py), (x+w, py), 1)
        
        if not self.pwr_hv:
            draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.2)
            return
        
        for _ in range(40):
            nx = random.randint(x, x+w-1)
            ny = random.randint(y, y+h-1)
            self.screen.set_at((nx, ny), C_FCR_NOISE)
        
        scale_y = (h / 2) / 1500
        scale_x = (w / 2) / 10
        
        if self.target.active and not self.target.crashed:
            td, taz, tel = self.target.get_polar()
            range_diff = td - self.range_gate
            
            if abs(range_diff) < 1500:
                az_diff = get_angle_diff(taz, self.ant_az)
                el_diff = tel - self.ant_el
                
                if abs(az_diff) < 15:
                    py = cy - range_diff * scale_y
                    px = cx + el_diff * scale_x
                    
                    if x < px < x+w and y < py < y+h:
                        intensity = 1.0 - abs(az_diff) / 15
                        for _ in range(int(50 * intensity * self.target.rcs)):
                            rx = px + random.gauss(0, 4)
                            ry = py + random.gauss(0, 8)
                            if x < rx < x+w and y < ry < y+h:
                                self.screen.set_at((int(rx), int(ry)), C_FCR_TARGET)
        
        for m in self.active_missiles:
            md, maz, mel = m.get_polar()
            m_range_diff = md - self.range_gate
            
            if abs(m_range_diff) < 1500:
                m_az_diff = get_angle_diff(maz, self.ant_az)
                m_el_diff = mel - self.ant_el
                
                if abs(m_az_diff) < 20:
                    mpy = cy - m_range_diff * scale_y
                    mpx = cx + m_el_diff * scale_x
                    
                    if x < mpx < x+w and y < mpy < y+h:
                        for _ in range(30):
                            rx = mpx + random.gauss(0, 2)
                            ry = mpy + random.gauss(0, 4)
                            if x < rx < x+w and y < ry < y+h:
                                self.screen.set_at((int(rx), int(ry)), C_FCR_MISSILE)
        
        draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.2)

    def draw_scope_i2(self, x, y, w, h):
        """И2显示器 - 搜索 CRT"""
        draw_crt_display(self.screen, (x, y, w, h), f"I2 {self.max_range//1000}KM")
        pygame.draw.rect(self.screen, C_FCR_BG, (x, y, w, h))
        
        if not self.pwr_sys:
            draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.2)
            return
        
        cx = x + w // 2
        max_range = self.max_range
        
        pygame.draw.line(self.screen, C_FCR_GRID, (cx, y), (cx, y+h), 1)
        
        tick_interval = 10000 if max_range == 80000 else 5000
        for r in range(tick_interval, int(max_range)+1, tick_interval):
            py = y + h - (r / max_range) * h
            pygame.draw.line(self.screen, C_FCR_GRID, (x, py), (x+8, py), 1)
            pygame.draw.line(self.screen, C_FCR_GRID, (x+w-8, py), (x+w, py), 1)
            
            km = r // 1000
            txt = self.font_sm.render(str(km), True, (60, 140, 70))
            self.screen.blit(txt, (x + w - 22, int(py) - 5))
        
        gate_y = y + h - (self.range_gate / max_range) * h
        if y < gate_y < y + h:
            pygame.draw.line(self.screen, C_FCR_STROBE, (x, gate_y), (x+w, gate_y), 2)
            gate_half = (1500 / max_range) * h
            pygame.draw.rect(self.screen, (*C_FCR_STROBE[:3], 30),
                           (x, gate_y - gate_half, w, gate_half * 2), 1)
        
        if not self.pwr_hv:
            draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.2)
            return
        
        if not self.sw_sdc:
            clutter_h = 20
            for i in range(x, x+w, 2):
                ch = random.randint(0, clutter_h)
                pygame.draw.line(self.screen, C_FCR_NOISE, (i, y+h), (i, y+h-ch), 1)
        
        scale_y = h / max_range
        scale_x = (w / 2) / 20
        
        if self.scanning and self.pwr_hv:
            scan_x = cx + self.scan_angle * scale_x
            pygame.draw.line(self.screen, C_FCR_SCAN, (scan_x, y), (scan_x, y+h), 1)
        
        if self.target.active and not self.target.crashed:
            td, taz, _ = self.target.get_polar()
            
            if td < max_range:
                az_diff = get_angle_diff(taz, self.ant_az)
                
                if abs(az_diff) < 25:
                    should_draw = True
                    if self.sw_sdc:
                        radial_v = abs(self.target.get_radial_velocity())
                        if radial_v < 30:
                            should_draw = False
                    
                    if should_draw:
                        py = y + h - td * scale_y
                        px = cx + az_diff * scale_x
                        
                        if x < px < x+w and y < py < y+h:
                            for _ in range(int(25 * self.target.rcs)):
                                rx = px + random.gauss(0, 3)
                                ry = py + random.gauss(0, 5)
                                if x < rx < x+w and y < ry < y+h:
                                    self.screen.set_at((int(rx), int(ry)), C_FCR_TARGET)
        
        for m in self.active_missiles:
            md, maz, _ = m.get_polar()
            if md < max_range:
                maz_diff = get_angle_diff(maz, self.ant_az)
                
                if abs(maz_diff) < 30:
                    mpy = y + h - md * scale_y
                    mpx = cx + maz_diff * scale_x
                    
                    if x < mpx < x+w and y < mpy < y+h:
                        pygame.draw.circle(self.screen, C_FCR_MISSILE, (int(mpx), int(mpy)), 2)
        
        draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.2)

    def draw_tv_display(self, x, y, w, h):
        """TV光学显示器 - 绿色夜视CRT"""
        draw_crt_display(self.screen, (x, y, w, h), "TOV 9Sh33A")
        pygame.draw.rect(self.screen, (5, 10, 5), (x, y, w, h))
        
        if not self.pwr_sys:
            draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.2)
            return
        
        fov = 5.0 if self.sw_tv_fov == 1 else 20.0
        zoom = 20.0 / fov
        
        cx, cy = x + w/2, y + h/2
        
        clip = pygame.Rect(x, y, w, h)
        self.screen.set_clip(clip)
        
        hz_y = cy + (self.ant_el * (h/fov))
        pygame.draw.rect(self.screen, C_TV_SKY, (x, y, w, h))
        if hz_y < y + h:
            pygame.draw.rect(self.screen, C_TV_GROUND, (x, max(y, hz_y), w, y+h - max(y, hz_y)))
        
        def project(ox, oy, oz):
            g = math.sqrt(ox**2 + oy**2)
            d = math.sqrt(ox**2 + oy**2 + oz**2)
            az = math.degrees(math.atan2(ox, -oy))
            az = normalize_angle(az)
            el = math.degrees(math.atan2(oz, g)) if g > 0 else 90
            
            az_err = get_angle_diff(az, self.ant_az)
            el_err = el - self.ant_el
            
            if abs(az_err) < fov and abs(el_err) < fov and d > 100:
                px = cx + az_err * (w / fov)
                py = cy - el_err * (h / fov)
                scale = (8000 / d) * zoom
                return px, py, scale
            return None
        
        for p in self.target.smoke_particles:
            res = project(p['x'], p['y'], p['z'])
            if res:
                px, py, s = res
                if x < px < x+w and y < py < y+h:
                    alpha = int(p['alpha'] * 120)
                    size = int(s * 2 * p['size'])
                    if size > 0:
                        smoke = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                        pygame.draw.circle(smoke, (40, 90, 40, alpha), (size, size), size)
                        self.screen.blit(smoke, (px-size, py-size))
        
        if self.target.active:
            res = project(self.target.x, self.target.y, self.target.z)
            if res:
                px, py, s = res
                if x < px < x+w and y < py < y+h:
                    if self.target.hit:
                        if int(pygame.time.get_ticks() / 80) % 2:
                            pygame.draw.circle(self.screen, C_PHOSPHOR_GREEN, (int(px), int(py)), int(s*2.5))
                    else:
                        if self.target.type == SCENARIO_F4E:
                            pygame.draw.ellipse(self.screen, (30, 90, 30),
                                              (px-s*1.5, py-s*0.3, s*3, s*0.6))
                            pygame.draw.polygon(self.screen, (25, 80, 25), [
                                (px-s*0.5, py), (px+s*0.5, py),
                                (px+s*1.5, py+s*0.8), (px-s*1.5, py+s*0.8)
                            ])
                        else:
                            pygame.draw.rect(self.screen, (25, 80, 25),
                                           (px-s, py-s*0.4, s*2, s*0.8))
        
        for m in self.active_missiles:
            trail_pts = []
            for tx, ty, tz in m.trail[-20:]:
                tres = project(tx, ty, tz)
                if tres:
                    tpx, tpy, _ = tres
                    if x < tpx < x+w and y < tpy < y+h:
                        trail_pts.append((int(tpx), int(tpy)))
            
            if len(trail_pts) > 1:
                pygame.draw.lines(self.screen, (160, 255, 160), False, trail_pts, 1)
            
            res = project(m.x, m.y, m.z)
            if res:
                px, py, s = res
                glow = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(glow, (120, 255, 120, 120), (15, 15), int(s*3+5))
                self.screen.blit(glow, (px-15, py-15), special_flags=pygame.BLEND_ADD)
                pygame.draw.circle(self.screen, (220, 255, 220), (int(px), int(py)), max(2, int(s)))
        
        self.screen.set_clip(None)
        
        gap, length = 15, 35
        pygame.draw.line(self.screen, C_TV_RETICLE, (cx-length, cy), (cx-gap, cy), 2)
        pygame.draw.line(self.screen, C_TV_RETICLE, (cx+gap, cy), (cx+length, cy), 2)
        pygame.draw.line(self.screen, C_TV_RETICLE, (cx, cy-length), (cx, cy-gap), 2)
        pygame.draw.line(self.screen, C_TV_RETICLE, (cx, cy+gap), (cx, cy+length), 2)
        
        pygame.draw.line(self.screen, C_TV_RETICLE, (cx-length, cy-5), (cx-length, cy+5), 1)
        pygame.draw.line(self.screen, C_TV_RETICLE, (cx+length, cy-5), (cx+length, cy+5), 1)
        
        mag = self.font_sm.render(f"x{int(zoom)}", True, C_PHOSPHOR_GREEN)
        self.screen.blit(mag, (x + 5, y + 5))
        
        draw_crt_effect(self.screen, (x, y, w, h), scanline_spacing=2, intensity=0.18)

    def draw_panel_launch(self, x, y, w, h):
        """发射控制面板 - 金属外壳"""
        draw_metal_panel(self.screen, (x, y, w, h), "UK-31M1 LAUNCH CONTROL")
        
        grid_x = x + 45
        grid_y = y + 45
        cell_w = 58
        cell_h = 26
        
        headers = ["I", "II", "III", "IV"]
        for i, hdr in enumerate(headers):
            txt = self.font_sm.render(hdr, True, C_TEXT_LABEL)
            self.screen.blit(txt, (grid_x + i*cell_w + cell_w//2 - txt.get_width()//2, grid_y))
        
        row_labels = ["MIS", "RDY", "BLK"]
        for row, label in enumerate(row_labels):
            ly = grid_y + 24 + row * cell_h
            txt = self.font_sm.render(label, True, C_TEXT_DIM)
            self.screen.blit(txt, (grid_x - 32, ly + 5))
            
            for col in range(4):
                launcher = self.launchers.launchers[col]
                cx_cell = grid_x + col * cell_w + cell_w//2
                cy_cell = ly + cell_h//2
                
                is_selected = col == self.launchers.selected
                cell_color = (45, 65, 45) if is_selected else (28, 35, 32)
                pygame.draw.rect(self.screen, cell_color,
                               (grid_x + col*cell_w + 2, ly + 2, cell_w - 4, cell_h - 4), border_radius=2)
                
                if is_selected:
                    pygame.draw.rect(self.screen, C_PHOSPHOR_GREEN,
                                   (grid_x + col*cell_w + 2, ly + 2, cell_w - 4, cell_h - 4), 2, border_radius=2)
                
                if row == 0:
                    count = launcher['missiles']
                    color = C_LAMP_GREEN if count > 0 else C_LAMP_OFF
                    txt = self.font_sm.render(str(count), True, color)
                    self.screen.blit(txt, (cx_cell - txt.get_width()//2, cy_cell - txt.get_height()//2))
                elif row == 1:
                    if launcher['ready']:
                        pygame.draw.circle(self.screen, C_LAMP_GREEN, (cx_cell, cy_cell), 6)
                    elif launcher['prep_timer'] > 0:
                        txt = self.font_sm.render(f"{launcher['prep_timer']:.0f}", True, C_LAMP_YELLOW)
                        self.screen.blit(txt, (cx_cell - txt.get_width()//2, cy_cell - txt.get_height()//2))
                elif row == 2:
                    can_fire, reason = self.launchers.can_fire(col, self.ant_az)
                    if not can_fire and reason == "BLOCKED":
                        pygame.draw.circle(self.screen, C_LAMP_RED, (cx_cell, cy_cell), 6)
        
        total = self.launchers.get_total_missiles()
        total_y = y + 145
        pygame.draw.rect(self.screen, C_RECESS, (x + 20, total_y, w - 40, 38), border_radius=2)
        total_txt = self.font_lg.render(f"TOTAL: {total}", True, C_PHOSPHOR_RED if total < 4 else C_PHOSPHOR_GREEN)
        self.screen.blit(total_txt, (x + w//2 - total_txt.get_width()//2, total_y + 6))
        
        sw_y = y + 210
        center_x = x + w // 2
        draw_metal_switch(self.screen, center_x - 90, sw_y, "SALVO", "SGL", self.sw_salvo == 2, self.font_sm)
        draw_metal_switch(self.screen, center_x, sw_y, "AUTO", "MAN", self.sw_auto, self.font_sm)
        draw_metal_switch(self.screen, center_x + 90, sw_y, "HV ON", "OFF", self.pwr_hv, self.font_sm)
        
        lamp_y = y + 295
        draw_illuminated_lamp(self.screen, center_x - 90, lamp_y, "READY", C_LAMP_GREEN,
                        self.launchers.launchers[self.launchers.selected]['ready'], self.font_sm)
        draw_illuminated_lamp(self.screen, center_x, lamp_y, "INHIBIT", C_LAMP_RED,
                        not self.launchers.can_fire(self.launchers.selected, self.ant_az)[0], self.font_sm)
        draw_illuminated_lamp(self.screen, center_x + 90, lamp_y, "FAIL", C_LAMP_ORANGE,
                        len(self.active_missiles) >= 2, self.font_sm)
        
        in_envelope = self.check_launch_envelope() and self.locked
        draw_illuminated_lamp(self.screen, x + w//2, y + 370, "AUTHORIZATION", C_LAMP_YELLOW, in_envelope, self.font_sm)
        
        btn_active = in_envelope and self.launchers.launchers[self.launchers.selected]['ready'] and self.pwr_hv
        draw_metal_button(self.screen, x + w//2, y + 460, "FIRE", btn_active, self.font, 35)
        
        prep_hint = self.font_sm.render("F1-F4: PREPARE", True, C_TEXT_DIM)
        self.screen.blit(prep_hint, (x + w//2 - prep_hint.get_width()//2, y + 520))

    def draw_panel_controls(self, x, y, w, h):
        """电源控制面板 - 金属外壳"""
        draw_metal_panel(self.screen, (x, y, w, h), "POWER CONTROL")
        
        sw_y = y + 55
        sw_spacing = 70
        
        draw_metal_switch(self.screen, x + 40, sw_y, "[1]", "GRID", self.sw_grid, self.font_sm)
        draw_metal_switch(self.screen, x + 40 + sw_spacing, sw_y, "[2]", "SYS", self.sw_sys, self.font_sm)
        draw_metal_switch(self.screen, x + 40 + sw_spacing*2, sw_y, "[3]", "HV", self.sw_hv, self.font_sm)
        draw_metal_switch(self.screen, x + 40 + sw_spacing*3, sw_y, "[4]", "ANT", self.sw_ant, self.font_sm)
        
        lamp_y = y + 135
        draw_illuminated_lamp(self.screen, x + 40, lamp_y, "D", C_LAMP_GREEN, self.pwr_grid, self.font_sm)
        draw_illuminated_lamp(self.screen, x + 40 + sw_spacing, lamp_y, "K", C_LAMP_GREEN, self.pwr_sys, self.font_sm)
        draw_illuminated_lamp(self.screen, x + 40 + sw_spacing*2, lamp_y, "V", C_LAMP_RED, self.pwr_hv, self.font_sm)
        draw_illuminated_lamp(self.screen, x + 40 + sw_spacing*3, lamp_y, "P", C_LAMP_GREEN, self.pwr_ant, self.font_sm)
        
        # 日志终端 - 内嵌CRT风格
        log_y = y + 200
        log_h = h - 280
        draw_crt_display(self.screen, (x + 8, log_y, w - 16, log_h), "SYSTEM LOG")
        pygame.draw.rect(self.screen, (6, 10, 6), (x + 8, log_y, w - 16, log_h))
        
        for i, msg in enumerate(self.log):
            color = C_TERM_GREEN if i == len(self.log) - 1 else C_TERM_DIM
            prefix = ">>> " if i == len(self.log) - 1 else "    "
            txt = self.font_sm.render(f"{prefix}{msg}", True, color)
            self.screen.blit(txt, (x + 15, log_y + 12 + i * 16))
        
        draw_crt_effect(self.screen, (x + 8, log_y, w - 16, log_h), scanline_spacing=2, intensity=0.12)
        
        hints = [
            "ARROWS: Antenna",
            "W/S: Range Gate",
            "SPACE: Fire",
            "P: Plot Board"
        ]
        hint_y = y + h - 75
        for i, hint in enumerate(hints):
            txt = self.font_sm.render(hint, True, C_TEXT_DIM)
            self.screen.blit(txt, (x + 15, hint_y + i * 16))

    def draw_panel_status(self, x, y, w, h):
        """状态面板 - 金属外壳"""
        draw_metal_panel(self.screen, (x, y, w, h), "APPROACH LAUNCH ZONE")
        
        scope_x = x + 15
        scope_y = y + 35
        scope_w = 250
        scope_h = 250
        
        draw_crt_display(self.screen, (scope_x, scope_y, scope_w, scope_h), "TACTICAL SCOPE")
        pygame.draw.rect(self.screen, C_RECESS, (scope_x, scope_y, scope_w, scope_h))
        
        cx = scope_x + scope_w // 2
        cy = scope_y + scope_h // 2
        scale = scope_w / 60000
        
        for r in [5000, 10000, 15000, 20000, 25000]:
            pygame.draw.circle(self.screen, (35, 55, 40), (cx, cy), int(r * scale), 1)
        
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            ex = cx + 25000 * scale * math.sin(rad)
            ey = cy - 25000 * scale * math.cos(rad)
            pygame.draw.line(self.screen, (25, 45, 30), (cx, cy), (ex, ey), 1)
        
        for launcher in self.launchers.launchers:
            az = launcher['azimuth']
            rad = math.radians(az)
            px = cx + 30 * math.sin(rad)
            py = cy - 30 * math.cos(rad)
            color = C_LAMP_GREEN if launcher['ready'] else (50, 60, 55)
            pygame.draw.circle(self.screen, color, (int(px), int(py)), 5)
        
        ant_rad = math.radians(self.ant_az)
        ax = cx + 20000 * scale * math.sin(ant_rad)
        ay = cy - 20000 * scale * math.cos(ant_rad)
        pygame.draw.line(self.screen, C_LAMP_YELLOW, (cx, cy), (ax, ay), 2)
        
        if self.target.active:
            td, taz, _ = self.target.get_polar()
            if td < 30000:
                trad = math.radians(taz)
                tx = cx + td * scale * math.sin(trad)
                ty = cy - td * scale * math.cos(trad)
                
                vscale = scale * 100
                vx = tx + self.target.vx * vscale
                vy = ty + self.target.vy * vscale
                pygame.draw.line(self.screen, C_LAMP_RED, (tx, ty), (vx, vy), 1)
                
                pygame.draw.circle(self.screen, C_LAMP_RED, (int(tx), int(ty)), 4)
                
                if self.locked:
                    time_to_impact = td / 780
                    impact_x = self.target.x + self.target.vx * time_to_impact
                    impact_y = self.target.y + self.target.vy * time_to_impact
                    impact_d = math.sqrt(impact_x**2 + impact_y**2)
                    impact_az = math.atan2(impact_x, -impact_y)
                    
                    ix = cx + impact_d * scale * math.sin(impact_az)
                    iy = cy - impact_d * scale * math.cos(impact_az)
                    
                    pygame.draw.circle(self.screen, C_TERM_CYAN, (int(ix), int(iy)), 8, 1)
                    pygame.draw.circle(self.screen, C_LAMP_GREEN, (cx, cy), int(25000 * scale), 1)
                    pygame.draw.circle(self.screen, C_LAMP_YELLOW, (cx, cy), int(3500 * scale), 1)
        
        for m in self.active_missiles:
            md, maz, _ = m.get_polar()
            if md < 30000:
                mrad = math.radians(maz)
                mx = cx + md * scale * math.sin(mrad)
                my = cy - md * scale * math.cos(mrad)
                pygame.draw.circle(self.screen, C_TERM_CYAN, (int(mx), int(my)), 3)
        
        # 图例
        legend_x = scope_x + scope_w + 12
        legend_y = scope_y + 5
        
        legends = [
            ("--", C_LAMP_YELLOW, "Azimuth"),
            ("O", C_LAMP_RED, "Target"),
            ("O", C_TERM_CYAN, "Missile"),
            ("O", C_LAMP_GREEN, "Rmax"),
            ("O", C_LAMP_YELLOW, "Rmin"),
        ]
        
        for i, (sym, col, desc) in enumerate(legends):
            txt = self.font_sm.render(f"{sym} {desc}", True, col)
            self.screen.blit(txt, (legend_x, legend_y + i * 20))
        
        # 目标信息 - 金属面板内数据块
        info_x = legend_x + 110
        info_y = scope_y
        info_w = 250
        info_h = 250
        
        draw_metal_panel(self.screen, (info_x, info_y, info_w, info_h), "TARGET DATA")
        
        info_lines = [
            f"TGT: {self.target.name}",
            f"RCS: {self.target.rcs:.2f} m2"
        ]
        
        if self.target.active:
            td, taz, tel = self.target.get_polar()
            rv = self.target.get_radial_velocity()
            info_lines.extend([
                f"RNG: {td/1000:.1f} km",
                f"AZ: {taz:.1f} deg",
                f"EL: {tel:.1f} deg",
                f"ALT: {self.target.z/1000:.2f} km",
                f"VR: {rv:.0f} m/s"
            ])
        
        for i, line in enumerate(info_lines):
            txt = self.font_sm.render(line, True, C_TEXT_MAIN)
            self.screen.blit(txt, (info_x + 10, info_y + 30 + i * 22))
        
        # 导弹状态
        missile_x = info_x + info_w + 12
        missile_y = scope_y
        missile_w = 200
        missile_h = 250
        
        draw_metal_panel(self.screen, (missile_x, missile_y, missile_w, missile_h), "IN FLIGHT")
        
        missile_title = self.font_sm.render("ACTIVE MISSILES:", True, C_PHOSPHOR_CYAN)
        self.screen.blit(missile_title, (missile_x + 10, missile_y + 30))
        
        for i, m in enumerate(self.active_missiles[:8]):
            md, _, _ = m.get_polar()
            fuel_pct = m.fuel / m.total_fuel * 100
            status = f"M{i+1}: {md/1000:.1f}km F:{fuel_pct:.0f}%"
            txt = self.font_sm.render(status, True, C_TEXT_MAIN)
            self.screen.blit(txt, (missile_x + 10, missile_y + 50 + i * 18))

    def draw_plotting_board(self):
        """绘图板叠加层"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        board_w, board_h = 720, 720
        board_x = (SCREEN_WIDTH - board_w) // 2
        board_y = (SCREEN_HEIGHT - board_h) // 2
        
        draw_metal_panel(self.screen, (board_x, board_y, board_w, board_h), "TACTICAL PLOTTING BOARD")
        
        cx = board_x + board_w // 2
        cy = board_y + board_h // 2
        scale = (board_w / 2) / 100000
        
        for r in [25000, 50000, 75000, 100000]:
            pygame.draw.circle(self.screen, (35, 60, 40), (cx, cy), int(r * scale), 1)
        
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            ex = cx + 100000 * scale * math.sin(rad)
            ey = cy - 100000 * scale * math.cos(rad)
            pygame.draw.line(self.screen, (30, 55, 35), (cx, cy), (ex, ey), 1)
        
        pygame.draw.circle(self.screen, C_TERM_CYAN, (cx, cy), 8)
        
        if len(self.target.history) > 1:
            pts = [(cx + hx * scale, cy + hy * scale) for hx, hy in self.target.history]
            pygame.draw.lines(self.screen, C_TERM_RED, False, pts, 2)
        
        if self.target.active:
            tx = cx + self.target.x * scale
            ty = cy + self.target.y * scale
            pygame.draw.circle(self.screen, C_TERM_RED, (int(tx), int(ty)), 6)
            
            td, taz, _ = self.target.get_polar()
            info = f"{self.target.name}: {td/1000:.1f}km / {self.target.z/1000:.1f}km"
            txt = self.font.render(info, True, C_TERM_RED)
            self.screen.blit(txt, (tx + 10, ty - 10))
        
        for m in self.active_missiles:
            if len(m.history) > 1:
                pts = [(cx + hx * scale, cy + hy * scale) for hx, hy in m.history]
                pygame.draw.lines(self.screen, C_TERM_CYAN, False, pts, 1)
            
            mx = cx + m.x * scale
            my = cy + m.y * scale
            pygame.draw.circle(self.screen, C_TERM_CYAN, (int(mx), int(my)), 4)
        
        hint = self.font.render("[P] CLOSE", True, C_TEXT_DIM)
        self.screen.blit(hint, (cx - hint.get_width()//2, board_y + board_h - 28))

    def draw_menu(self):
        """主菜单 - 金属机箱中的CRT终端"""
        draw_chassis_background(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        cx = SCREEN_WIDTH // 2
        
        # 旋转扫描线装饰
        rad = math.radians(self.p18_angle)
        sweep = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(sweep, (0, 60, 25, 50), (cx, 300),
                        (cx + 800 * math.sin(rad), 300 - 800 * math.cos(rad)), 2)
        self.screen.blit(sweep, (0, 0))
        
        # 主金属面板
        panel_w, panel_h = 700, 520
        panel_x = cx - panel_w // 2
        panel_y = 110
        
        draw_metal_panel(self.screen, (panel_x, panel_y, panel_w, panel_h), "MAIN SYSTEM")
        
        # 内部CRT显示区域
        crt_x = panel_x + 20
        crt_y = panel_y + 35
        crt_w = panel_w - 40
        crt_h = panel_h - 60
        draw_crt_display(self.screen, (crt_x, crt_y, crt_w, crt_h))
        pygame.draw.rect(self.screen, C_TERM_BG, (crt_x, crt_y, crt_w, crt_h))
        
        # 标题
        title_y = crt_y + 40
        title1 = self.font_title.render("S-125 NEVA", True, C_TERM_GREEN)
        title2 = self.font_title_sm.render("SA-3 GOA SAM SIMULATOR", True, C_TERM_DIM)
        
        self.screen.blit(title1, (cx - title1.get_width()//2, title_y))
        self.screen.blit(title2, (cx - title2.get_width()//2, title_y + 55))
        
        pygame.draw.line(self.screen, C_TERM_DIM, (crt_x + 50, title_y + 95), (crt_x + crt_w - 50, title_y + 95), 1)
        
        # 菜单选项
        menu_font = pygame.font.SysFont("consolas", 24, bold=True)
        options = [
            ("[1] START MISSION", C_TERM_GREEN),
            ("[2] OPERATOR MANUAL", C_TEXT_LABEL),
            ("[3] EXIT SYSTEM", C_TEXT_DIM)
        ]
        
        start_y = title_y + 120
        for i, (opt, color) in enumerate(options):
            txt = menu_font.render(opt, True, color)
            self.screen.blit(txt, (cx - txt.get_width()//2, start_y + i * 65))
        
        if int(pygame.time.get_ticks() / 500) % 2:
            status = self.font.render("SYSTEM STANDBY...", True, C_TERM_CYAN)
            self.screen.blit(status, (cx - status.get_width()//2, crt_y + crt_h - 50))
        
        draw_crt_effect(self.screen, (crt_x, crt_y, crt_w, crt_h), scanline_spacing=2, intensity=0.15)
        
        # 版本信息（刻在机箱上）
        ver = self.font_sm.render("v2.4.1 // SOVIET AIR DEFENSE SYSTEM", True, C_TEXT_DIM)
        self.screen.blit(ver, (cx - ver.get_width()//2, SCREEN_HEIGHT - 35))

    def draw_briefing(self):
        """任务简报 - 金属机箱中的CRT终端"""
        draw_chassis_background(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        doc_w, doc_h = 920, 760
        doc_x = (SCREEN_WIDTH - doc_w) // 2
        doc_y = (SCREEN_HEIGHT - doc_h) // 2
        
        draw_metal_panel(self.screen, (doc_x, doc_y, doc_w, doc_h), "MISSION BRIEFING")
        
        # CRT显示区域
        crt_x = doc_x + 15
        crt_y = doc_y + 35
        crt_w = doc_w - 30
        crt_h = doc_h - 55
        draw_crt_display(self.screen, (crt_x, crt_y, crt_w, crt_h))
        pygame.draw.rect(self.screen, (10, 14, 10), (crt_x, crt_y, crt_w, crt_h))
        
        header = self.font_lg.render("SELECT TARGET SCENARIO", True, C_TEXT_MAIN)
        self.screen.blit(header, (crt_x + crt_w//2 - header.get_width()//2, crt_y + 20))
        
        pygame.draw.line(self.screen, C_TERM_DIM, (crt_x + 40, crt_y + 50), (crt_x + crt_w - 40, crt_y + 50), 1)
        
        scenarios = [
            {
                "key": "[1]",
                "name": "SCENARIO A: UAV INTERCEPT",
                "target": "MQM-107 STREAKER",
                "rcs": "1.0 m2",
                "alt": "3-6 km",
                "threat": "Training/Standard",
                "color": C_PHOSPHOR_GREEN
            },
            {
                "key": "[2]",
                "name": "SCENARIO B: FIGHTER-BOMBER",
                "target": "F-4E PHANTOM II",
                "rcs": "6.0 m2",
                "alt": "0.5-8 km",
                "threat": "High (High G)",
                "color": C_PHOSPHOR_AMBER
            },
            {
                "key": "[3]",
                "name": "SCENARIO C: STEALTH TARGET",
                "target": "F-117A NIGHTHAWK",
                "rcs": "0.025 m2",
                "alt": "3-5 km",
                "threat": "Extreme (Stealth)",
                "color": C_PHOSPHOR_RED
            }
        ]
        
        y_offset = crt_y + 70
        for scenario in scenarios:
            box_h = 160
            pygame.draw.rect(self.screen, (15, 22, 15), (crt_x + 40, y_offset, crt_w - 80, box_h), border_radius=3)
            pygame.draw.rect(self.screen, scenario["color"], (crt_x + 40, y_offset, crt_w - 80, box_h), 1, border_radius=3)
            
            key_txt = self.font_lg.render(scenario["key"], True, scenario["color"])
            name_txt = self.font_md.render(scenario["name"], True, scenario["color"])
            self.screen.blit(key_txt, (crt_x + 60, y_offset + 15))
            self.screen.blit(name_txt, (crt_x + 120, y_offset + 18))
            
            info_lines = [
                f"Target: {scenario['target']}",
                f"RCS: {scenario['rcs']}",
                f"Alt: {scenario['alt']}",
                f"Threat: {scenario['threat']}"
            ]
            
            for i, line in enumerate(info_lines):
                txt = self.font.render(line, True, C_TEXT_MAIN)
                self.screen.blit(txt, (crt_x + 80, y_offset + 50 + i * 24))
            
            y_offset += box_h + 20
        
        hint = self.font.render("[ESC] Return to Menu", True, C_TEXT_DIM)
        self.screen.blit(hint, (crt_x + crt_w//2 - hint.get_width()//2, crt_y + crt_h - 30))
        
        draw_crt_effect(self.screen, (crt_x, crt_y, crt_w, crt_h), scanline_spacing=2, intensity=0.12)

    def draw_debriefing(self):
        """任务汇报 - 金属机箱中的CRT终端"""
        draw_chassis_background(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        header = self.font_title_sm.render("COMBAT RESULTS", True, C_TEXT_MAIN)
        self.screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, 25))
        
        result = self.report["result"]
        if "DESTROYED" in result:
            result_color = C_PHOSPHOR_GREEN
        elif "LOST" in result or "ESCAPED" in result:
            result_color = C_PHOSPHOR_RED
        else:
            result_color = C_PHOSPHOR_AMBER
        
        result_txt = self.font_title_sm.render(f"OUTCOME: {result}", True, result_color)
        self.screen.blit(result_txt, (SCREEN_WIDTH//2 - result_txt.get_width()//2, 75))
        
        # 数据面板
        panel_x = 60
        panel_y = 150
        panel_w = 440
        panel_h = 340
        
        draw_metal_panel(self.screen, (panel_x, panel_y, panel_w, panel_h), "ENGAGEMENT DATA")
        
        data_lines = [
            f"Target: {self.target.name}",
            f"RCS: {self.target.rcs:.3f} m2",
            f"Missiles Fired: {self.report['missiles_fired']}",
            f"Lock Range: {self.report['lock_range']} m",
            f"Hit Range: {self.report['hit_range']} m",
        ]
        
        for i, line in enumerate(data_lines):
            txt = self.font_md.render(line, True, C_TEXT_MAIN)
            self.screen.blit(txt, (panel_x + 20, panel_y + 35 + i * 38))
        
        # 轨迹图
        map_x = 530
        map_y = 150
        map_size = 500
        
        draw_metal_panel(self.screen, (map_x, map_y, map_size, map_size), "TRAJECTORY MAP")
        
        cx = map_x + map_size // 2
        cy = map_y + map_size // 2
        scale = (map_size / 2) / 80000
        
        for r in [20000, 40000, 60000]:
            pygame.draw.circle(self.screen, C_TERM_DIM, (cx, cy), int(r * scale), 1)
        
        pygame.draw.circle(self.screen, C_TERM_CYAN, (cx, cy), 5)
        
        if len(self.target.history) > 1:
            pts = [(cx + hx * scale, cy + hy * scale) for hx, hy in self.target.history]
            pygame.draw.lines(self.screen, C_TERM_RED, False, pts, 2)
            
            if pts:
                end_pt = pts[-1]
                pygame.draw.circle(self.screen, C_TERM_RED, (int(end_pt[0]), int(end_pt[1])), 5)
                
                if self.target.hit:
                    pygame.draw.line(self.screen, C_TERM_RED, 
                                   (end_pt[0]-8, end_pt[1]-8), (end_pt[0]+8, end_pt[1]+8), 2)
                    pygame.draw.line(self.screen, C_TERM_RED, 
                                   (end_pt[0]+8, end_pt[1]-8), (end_pt[0]-8, end_pt[1]+8), 2)
        
        for m in self.active_missiles:
            if len(m.history) > 1:
                mpts = [(cx + mx * scale, cy + my * scale) for mx, my in m.history]
                pygame.draw.lines(self.screen, C_TERM_CYAN, False, mpts, 1)
        
        legend_y = map_y + map_size + 20
        pygame.draw.circle(self.screen, C_TERM_CYAN, (map_x + 20, legend_y), 4)
        self.screen.blit(self.font_sm.render("Site", True, C_TERM_CYAN), (map_x + 35, legend_y - 6))
        
        pygame.draw.line(self.screen, C_TERM_RED, (map_x + 100, legend_y), (map_x + 130, legend_y), 2)
        self.screen.blit(self.font_sm.render("Tgt Track", True, C_TERM_RED), (map_x + 140, legend_y - 6))
        
        pygame.draw.line(self.screen, C_TERM_CYAN, (map_x + 230, legend_y), (map_x + 260, legend_y), 1)
        self.screen.blit(self.font_sm.render("Msl Track", True, C_TERM_CYAN), (map_x + 270, legend_y - 6))
        
        # 评价
        eval_y = 510
        draw_metal_panel(self.screen, (panel_x, eval_y, panel_w, 200), "PERFORMANCE RATING")
        
        if "DESTROYED" in result:
            if self.report['missiles_fired'] <= 2:
                grade = "EXCELLENT"
                grade_color = C_PHOSPHOR_GREEN
            elif self.report['missiles_fired'] <= 4:
                grade = "GOOD"
                grade_color = C_PHOSPHOR_AMBER
            else:
                grade = "SATISFACTORY"
                grade_color = C_PHOSPHOR_AMBER
        else:
            grade = "UNSATISFACTORY"
            grade_color = C_PHOSPHOR_RED
        
        grade_txt = self.font_lg.render(grade, True, grade_color)
        self.screen.blit(grade_txt, (panel_x + panel_w//2 - grade_txt.get_width()//2, eval_y + 65))
        
        if self.target.type == SCENARIO_F117:
            if "DESTROYED" in result:
                comment = "Stealth target killed! Excellent tactics."
            else:
                comment = "Stealth targets are hard to detect. Precision required."
        elif self.target.type == SCENARIO_F4E:
            if "DESTROYED" in result:
                comment = "High-speed intercept successful."
            else:
                comment = "F-4E has high speed and maneuverability."
        else:
            if "DESTROYED" in result:
                comment = "Standard target intercept successful."
            else:
                comment = "Basic operation training required."
        
        def blit_text_wrapped(surface, text, pos, font, color, max_width):
            words = text.split(' ')
            space = font.size(' ')[0]
            x, y = pos
            curr_line_w = 0
            
            for word in words:
                word_surface = font.render(word, True, color)
                word_w, word_h = word_surface.get_size()
                if curr_line_w + word_w >= max_width:
                    x = pos[0]
                    y += word_h + 4
                    curr_line_w = 0
                surface.blit(word_surface, (x, y))
                x += word_w + space
                curr_line_w += word_w + space

        blit_text_wrapped(self.screen, comment, (panel_x + 20, eval_y + 115), self.font, C_TEXT_MAIN, panel_w - 40)
        
        hint = self.font_lg.render("[ESC] Return to Menu", True, C_TERM_CYAN)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 780))

    def draw_manual(self):
        """操作手册 - 金属机箱中的CRT终端"""
        draw_chassis_background(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        doc_w = 1200
        doc_h = 840
        
        doc_x = (SCREEN_WIDTH - doc_w) // 2
        doc_y = (SCREEN_HEIGHT - doc_h) // 2
        
        draw_metal_panel(self.screen, (doc_x, doc_y, doc_w, doc_h), "OPERATOR MANUAL")
        
        # CRT显示区域
        crt_x = doc_x + 15
        crt_y = doc_y + 35
        crt_w = doc_w - 30
        crt_h = doc_h - 55
        draw_crt_display(self.screen, (crt_x, crt_y, crt_w, crt_h))
        pygame.draw.rect(self.screen, (10, 14, 10), (crt_x, crt_y, crt_w, crt_h))
        
        header = self.font_lg.render("S-125 NEVA OPERATING MANUAL", True, C_TEXT_MAIN)
        self.screen.blit(header, (crt_x + crt_w//2 - header.get_width()//2, crt_y + 20))
        
        pygame.draw.line(self.screen, C_TERM_DIM, (crt_x + 40, crt_y + 50), (crt_x + crt_w - 40, crt_y + 50), 1)
        
        left_x = crt_x + 40
        y = crt_y + 70
        line_h = 22
        
        sections = [
            ("// SYSTEM OVERVIEW", C_PHOSPHOR_CYAN, [
                "S-125 Neva (SA-3 Goa) is a low-to-medium altitude SAM system",
                "Composed of SNR-125M1 Fire Control Radar and V-601P Missiles",
            ]),
            ("// RADAR PARAMETERS", C_PHOSPHOR_CYAN, [
                "P-18 Acquisition Radar:",
                "  - Detection Range: 80km",
                "  - Function: Provides target azimuth and range",
                "SNR-125M1 Fire Control Radar:",
                "  - I2 Scope: Search Mode (0-80km or 0-40km)",
                "  - I1 Scope: Precision Tracking (+/- 1.5km)",
                "  - Max Tracking Range: 50km",
            ]),
            ("// MISSILE PARAMETERS (V-601P)", C_PHOSPHOR_CYAN, [
                "  - Max Speed: 780 m/s (Mach 2.3)",
                "  - Boost Time: 4s / Sustain Time: 22s",
                "  - Effective Range: 3.5 - 25 km",
                "  - Max Altitude: 18 km",
                "  - Prox Fuse: 50m",
            ]),
        ]
        
        for section_title, title_color, lines in sections:
            txt = self.font_md.render(section_title, True, title_color)
            self.screen.blit(txt, (left_x, y))
            y += line_h + 5
            
            for line in lines:
                color = C_PHOSPHOR_AMBER if line.startswith("  -") else C_TEXT_MAIN
                txt = self.font.render(line, True, color)
                self.screen.blit(txt, (left_x, y))
                y += line_h
            
            y += 10
        
        right_x = crt_x + 620
        y = crt_y + 70
        
        controls = [
            ("// PROCEDURES", C_PHOSPHOR_CYAN, [
                "[1] GRID - Grid Power",
                "[2] SYS - System Power", 
                "[3] HV - High Voltage/Transmitter",
                "[4] ANT - Antenna Servo",
                "",
                "[ARROWS] - Antenna Azimuth/Elevation",
                "[W/S] - Adjust Range Gate",
                "[SHIFT] - Fine Control",
                "",
                "[F1-F4] - Prepare Launcher I-IV (30s)",
                "[TAB] - Select Launcher",
                "[SPACE] - Fire Missile",
                "",
                "[R] - Range Mode 80/40km",
                "[M] - MTI (Moving Target Indicator)",
                "[G] - Guidance Method PS/TT",
                "[Z] - Salvo/Single",
                "[A] - Auto Fire",
                "[T] - TV Zoom",
                "[P] - Plotting Board",
            ]),
            ("// GUIDANCE METHODS", C_PHOSPHOR_CYAN, [
                "PS (Lead): Missile flies to predicted impact point",
                "  Used for normal targets",
                "TT (Three-Point): Missile stays on LOS to target",
                "  Used for jamming targets",
            ]),
            ("// LAUNCH INHIBIT CONDITIONS", C_PHOSPHOR_RED, [
                "- Launcher pointing at radar (+/- 30 deg)",
                "- Missile not ready",
                "- Target not locked",
                "- High Voltage not ON",
            ]),
        ]
        
        for section_title, title_color, lines in controls:
            txt = self.font_md.render(section_title, True, title_color)
            self.screen.blit(txt, (right_x, y))
            y += line_h + 5
            
            for line in lines:
                if line == "":
                    y += 5
                    continue
                if line.startswith("["):
                    color = C_PHOSPHOR_AMBER
                elif line.startswith("-"):
                    color = C_PHOSPHOR_RED
                else:
                    color = C_TEXT_MAIN
                txt = self.font.render(line, True, color)
                self.screen.blit(txt, (right_x, y))
                y += line_h
            
            y += 10
        
        hint = self.font_lg.render("[ESC] Return to Menu", True, C_TERM_CYAN)
        self.screen.blit(hint, (crt_x + crt_w//2 - hint.get_width()//2, crt_y + crt_h - 30))
        
        draw_crt_effect(self.screen, (crt_x, crt_y, crt_w, crt_h), scanline_spacing=2, intensity=0.1)


# ==========================================
# 主程序入口
# ==========================================

if __name__ == "__main__":
    simulator = SA3Simulator()
    simulator.run()
