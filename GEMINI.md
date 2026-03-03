# Robotic-arm-AI-training (GEMINI.md)

This project focuses on simulating and training AI agents for robotic control, specifically exploring a 2D robotic arm and a 3D drone using Reinforcement Learning.

## Project Overview

- **Purpose:** Diving into AI technology to simulate anthropomorphic manipulators and drone control.
- **Main Technologies:**
  - **Language:** Python
  - **RL Framework:** Stable-Baselines3 (PPO), Gymnasium
  - **2D Simulation:** Pygame
  - **3D Simulation:** PyBullet
  - **Mathematical Libraries:** NumPy

## Key Files and Directory Structure

- `2D_ROBOARM.py`: The main script for the 2D robotic arm simulation. It includes a custom `Gymnasium` environment and uses `PPO` from `Stable-Baselines3` for training/testing.
- `3D_DRONE_AI.py`: A `Gymnasium` environment for a 3D drone simulation using `PyBullet`. It handles 4-motor thrust and external force application.
- `drone_model.py`: A script that generates the `simple_drone.urdf` file using Python's `minidom` XML library.
- `simple_drone.urdf`: The URDF (Unified Robot Description Format) model file for the drone, defining its physical properties, links, and joints.
- `TEST_3D.py`: A basic test script to verify `PyBullet` connectivity and model loading (loads `r2d2.urdf` as a placeholder).
- `ppo_robot_arm.zip`: A saved model from a previous training session of the 2D robotic arm.
- `.venv/`: Python virtual environment containing the necessary dependencies.

## Building and Running

### Prerequisites

Ensure you have the following Python packages installed (usually handled by the local `.venv`):
- `gymnasium`
- `stable-baselines3`
- `numpy`
- `pygame`
- `pybullet`

### Running the Simulations

1.  **2D Robotic Arm:**
    - To train or test the agent: `python 2D_ROBOARM.py`
    - *Note:* Modify the `TRYB` variable in the `if __name__ == "__main__":` block to `"TRENING"` or `"TEST"`.

2.  **3D Drone Simulation:**
    - To update/regenerate the drone model: `python drone_model.py`
    - To run the drone simulation: `python 3D_DRONE_AI.py`

3.  **Basic 3D Test:**
    - To test PyBullet setup: `python TEST_3D.py`

## Development Conventions

- **Environments:** Follows the `Gymnasium` API (with `reset`, `step`, and `render` methods).
- **Naming:** Follows standard Python snake_case conventions.
- **Comments:** The code contains helpful comments in both English and Polish.
- **Physics:** PyBullet simulations use the `p.LINK_FRAME` and external force application for realism.
- **Rendering:** 2D rendering is handled by Pygame with a target FPS of 30.
