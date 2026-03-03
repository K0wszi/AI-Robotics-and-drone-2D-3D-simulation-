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
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        p.setAdditionalSearchPath(current_dir)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        # action of 4 motors - thrust
        self.action_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        # observation space: drone pov
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(12,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        p.resetSimulation()
        p.setGravity(0, 0, -9.81)
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        urdf_path = os.path.join(current_dir,"simple_drone.urdf")
        p.loadURDF("plane.urdf")
        self.drone_id = p.loadURDF(urdf_path, [0, 0, 1])
        return self._get_obs(), {}

    def _get_obs(self):
        # get positon & orientation from pybullet
        pos, orient = p.getBasePositionAndOrientation(self.drone_id)
        # get linear & angular veloci
        vel, ang_vel = p.getBaseVelocity(self.drone_id)
        # switching Euler quaternion to Euler's angle (roll, pithch, yaw)
        euler = p.getEulerFromQuaternion(orient)
        return np.array([*pos, *euler, *vel, *ang_vel], dtype=np.float32)
    
    def step(self, action):
        max_thrust = 14.0 #Newtons
        for i in range(4):
            thrust = action[i] * max_thrust
            p.applyExternalForce(
                self.drone_id, 
                i,
                [0, 0, thrust],
                [0, 0, 0],
                p.LINK_FRAME
            )
            
        p.stepSimulation()
        time.sleep(1./240.)

        obs = self._get_obs()
        pos = obs[0:3] #X,Y,Z
        euler = obs[3:6] #roll, pitch, yaw
        
        reward = -abs(pos[2] - 1.5) - 0.5*(abs(euler[0]) + abs(euler[1]))
        terminated = bool(pos[2] < 0.1 or pos[2] > 5.0)
        return obs, reward. terminated, False, {"height": pos[2]}

if __name__ == "__main__":
    env = DroneHoverEnv(render_mode=True)
    obs, info = env.reset()
    print("3D simulation is running!")
    try:
        while True:
            #Checking GUI connection
            if not p.isConnected():
                break

            action = [0.5, 0.5, 0.5, 0.5]
            obs, reward, terminated, truncated, info = env.step(action)
    except KeyboardInterrupt:
        print("Simulation ended")
    finally:
        if p.isConnected():
            p.disconnect()
        print("simulation ended succesfully")


            
