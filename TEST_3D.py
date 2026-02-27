import pybullet as p
import pybullet_data
import time
#connect with simulator
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath()) #adding path - ready models

p.setGravity(0, 0, -9.81)
planeId = p.loadURDF("plane.urdf")
#adding device
droneStartPos = [0, 0, 1]
droneStartOrientation = p.getQuaternionFromEuler([0, 0, 0])
droneId = p.loadURDF("r2d2.urdf", droneStartPos, droneStartOrientation)

print("3D Simulation is currently Running")
for i in range (10000):
    p.stepSimulation()
    time.sleep(1./240.)

p.disconnect()

