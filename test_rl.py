import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO

class RobotArmEnv(gym.Env):

    def __init__(self):
        super(RobotArmEnv, self).__init__()
        #parameters
        self.L1 = 1.0 # długość ramienia do 1 przegubu
        self.L2 = 1.0
        self.dt = 0.05 #50ms times step
        # [sin(q1), cos(q1), sin(q2), cos(q2), x_ee, y_ee, x_target, y_target]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32) #shape - tablica 2 na 1
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32)
        self.q1 = 0.0
        self.q2= 0.0
        self.q1_dot = 0.0 # velocity joint 1 
        self.q2_dot = 0.0 # velocity joint 2
        self.target_pos = np.array([1.5,0.5]) #reaching target

        #...symulacja
        self.screen_size = 600
        self.screen = None
        self.clock = None
        self.scale = 150


    def _get_obs(self):
        return np.array([
            np.cos(self.q1), np.sin(self.q1),
            np.cos(self.q2), np.sin(self.q2),
            self.target_pos[0], self.target_pos[1],
            self.q1_dot, self.q2_dot 
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        #obsluga seed - generator losowosci
        super().reset(seed=seed)
        #losowanie kątów startowych
        self.q1 = self.np_random.uniform(low=-np.pi, high=np.pi)
        self.q2 = self.np_random.uniform(low=-np.pi, high=np.pi)
        self.q1_dot = 0.0
        self.q2_dot = 0.0
        #Nowy cel w zaięgu ramienia
        self.target_pos = self.np_random.uniform(low=-1.5, high=1.5, size=(2,)).astype(np.float32)
        observation = self._get_obs()
        return observation, {}
    
    def step(self, action):
        
        self.q1_dot, self.q2_dot = action
        self.q1 += self.q1_dot * self.dt
        self.q2 += self.q2_dot * self.dt
        #kinematyka prosta - End-Effector
        current_x = self.L1 * np.cos(self.q1) + self.L2 * np.cos(self.q1 + self.q2)
        current_y = self.L1 * np.sin(self.q1) + self.L2 * np.sin(self.q1 + self.q2)
        #...........NAGRODA
        distance = np.sqrt((self.target_pos[0] - current_x)**2 + (self.target_pos[1] -current_y)**2)
        reward = -distance - 0.1
        #............warunki zakończenia
        terminated = bool(distance < 0.1)
        truncated = False #brak limitu kroków czasowych
        if terminated:
            reward += 100
        return self._get_obs(), reward, terminated, truncated, {"dist": distance}
    
    def render(self):
        import pygame
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
            self.clock = pygame.time.Clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        self.screen.fill((255, 255, 255))
        #.....Rysowanie
        cx, cy = self.screen_size // 2, self.screen_size // 2
        #.....1 przegub - pozycja
        p1_x = int(cx + (self.L1 * np.cos(self.q1)) * self.scale)
        p1_y = int(cy - (self.L1 * np.sin(self.q1)) * self.scale) # - bo odwrocona os
        #.....2 koniec ramienia - pozycja (end effector)
        ee_x = self.L1 * np.cos(self.q1) + self.L2 * np.cos(self.q1 + self.q2)
        ee_y = self.L1 * np.sin(self.q1) + self.L2 * np.sin(self.q1 + self.q2)

        ee_px = int(cx + ee_x * self.scale)
        ee_py = int(cy - ee_y * self.scale) # odwrocona oś

        #target
        tx = int(cx + self.target_pos[0] * self.scale)
        ty = int(cy - self.target_pos[1] * self.scale)
        pygame.draw.circle(self.screen, (255,0,0), (tx,ty), 10)
        pygame.draw.line(self.screen, (0,0,0), (cx, cy), (p1_x, p1_y), 5) 
        pygame.draw.line(self.screen, (0, 0, 255), (p1_x, p1_y), (ee_px,ee_py), 5)

        pygame.display.flip()
        self.clock.tick(30) #30 fps

    ##..................TRENING
if __name__ == "__main__":
    #instancja środowiska
    env = RobotArmEnv()
    model = PPO("MlpPolicy", env, verbose=1)
    #inicjalizacja modelu ppo
    print("Inicjalizacja modelu PP0")
    model.learn(total_timesteps=100000)
    print("\nTestowanie wytrenowanego agenta:")
    obs, info = env.reset()
    for i in range(10):
        terminated = False
        steps = 0
        while not terminated and steps < 100:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            steps += 1
            env.render()
        
        print (f"Próba {i+1}: Dystans końocwy = {info['dist']:.3f}m (Kroki: {steps})")
        obs, info = env.reset()
    



