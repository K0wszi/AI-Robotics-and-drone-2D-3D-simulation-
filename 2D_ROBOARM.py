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
        #end effector
        ee_x = self.L1 * np.cos(self.q1) + self.L2 * np.cos(self.q1 + self.q2)
        ee_y = self.L1 * np.sin(self.q1) + self.L2 * np.sin(self.q1 + self.q2)

        #blad pozycjonowania
        dx = self.target_pos[0] - ee_x
        dy = self.target_pos[1] - ee_y
        return np.array([
            np.cos(self.q1), np.sin(self.q1),
            np.cos(self.q2), np.sin(self.q2),
            dx, dy,
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
        #kinematyka PRZED 
        old_x = self.L1 * np.cos(self.q1) + self.L2 * np.cos(self.q1 + self.q2)
        old_y = self.L1 * np.sin(self.q1) + self.L2 * np.sin(self.q1 + self.q2)
        old_dist = np.sqrt((self.target_pos[0] - old_x)**2 + (self.target_pos[1] - old_y)**2)
        #wykonanie ruchu
        self.q1_dot, self.q2_dot = action
        self.q1 += self.q1_dot * self.dt
        self.q2 += self.q2_dot * self.dt
        #kinematyka prosta - End-Effector
        new_x = self.L1 * np.cos(self.q1) + self.L2 * np.cos(self.q1 + self.q2)
        new_y = self.L1 * np.sin(self.q1) + self.L2 * np.sin(self.q1 + self.q2)
        new_dist = np.sqrt((self.target_pos[0] - new_x)**2 + (self.target_pos[1] - new_y)**2)
        #...........NAGRODA za zblizenie sie do celu
        reward = (old_dist - new_dist) * 20.0
        #...........KARA za niefektywne wykorzystanie dostepnego czasu
        reward -= 0.01
        #............warunki zakończenia
        terminated = bool(new_dist < 0.1)
        if terminated:
            reward += 100

        truncated = False 
        return self._get_obs(), reward, terminated, truncated, {"dist": new_dist}
    
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
    env = RobotArmEnv()
    TRYB = "TEST"
    if TRYB == "TRENING":
        model = PPO("MlpPolicy", env, verbose=1)
        print("Training starts now...")
        model.learn(total_timesteps=150000)
        model.save("ppo_robot_arm")
        print("Training_model_saved")
    else:
        print("Loading Trainded Robot")
        model = PPO.load("ppo_robot_arm", env=env)
        
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
    



