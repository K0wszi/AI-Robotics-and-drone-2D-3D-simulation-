import pybullet as p
import pybullet_data
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time

class DroneHoverEnv(gym.Env):
    def __init__(self, render_mode=False):
        super().__init__()
        if render_mode:
            self.client = p.connect(p.GUI)
        else:
            self.client = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        # action of 4 motors - thrust
        self.action_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        # observation space: drone pov
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(12,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        p.resetSimulation()
        p.setGravity(0, 0, -9.81)
        self.plane_id = p.loadURDF("plane.urdf")
        self.drone_id = p.loadURDF("r2d2.urdf", [0, 0, 1])
        num_joints = p.getNumJoints(self.drone_id)
        print(f"Dron ma {num_joints} silników")
        return self._get_obs(),{}
        
    def _get_obs(self):
        # get positon & orientation from pybullet
        pos, orient = p.getBasePositionAndOrientation(self.drone_id)
        # get linear & angular veloci
        vel, ang_vel = p.getBaseVelocity(self.drone_id)
        # switching Euler quaternion to Euler's angle (roll, pithch, yaw)
        euler = p.getEulerFromQuaternion(orient)
        return np.array([*pos, *euler, *vel, *ang_vel], dtype=np.float32)
    
    def step(self, action):
        max_thrust = 50.0 #Newtons
        for i in range(4):
            thrust = action[i] * max_thrust
            p.applyExternalForce(self.drone_id, i, [0, 0, thrust], [0, 0, 0], p.LINK_FRAME)
        
        p.stepSimulation()
        time.sleep(1./240.)

        obs = self._get_obs()
        reward = 0
        terminated = False
        truncated = False
        
        return obs, reward, terminated, truncated, {}

    

if __name__ == "__main__":
    env = DroneHoverEnv(render_mode=True)
    obs, info = env.reset()
    print("3D simulation is running!")
    try:
        while True:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
    except KeyboardInterrupt:
        print("Simulation ended")



            
