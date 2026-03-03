from xml.dom import minidom

doc = minidom.Document()
robot = doc.createElement('robot')
robot.setAttribute('name', 'drone')
doc.appendChild(robot)

# FRAME
base_link = doc.createElement('link')
base_link.setAttribute('name','base_link')

#PHYSICS
b_inertial = doc.createElement('inertial')        
b_mass = doc.createElement('mass')
b_mass.setAttribute('value', '0.5')
b_inertial.appendChild(b_mass)

b_inertia = doc.createElement('inertia')      
for attr in ['ixx', 'iyy', 'izz']: b_inertia.setAttribute(attr, '0.01') 
for attr in ['ixy', 'ixz', 'iyz']: b_inertia.setAttribute(attr, '0')
b_inertial.appendChild(b_inertia)
base_link.appendChild(b_inertial)

#VISUAL LOOK - PLATFORM
visual = doc.createElement('visual')
geom = doc.createElement('geometry')
box = doc.createElement('box')
box.setAttribute('size', '0.4 0.4 0.05')
geom.appendChild(box)
visual.appendChild(geom)

mat = doc.createElement('material')
mat.setAttribute('name', 'dark_grey')
color = doc.createElement('color')
color.setAttribute('rgba', '0.2 0.2 0.2 1.0')
mat.appendChild(color)
visual.appendChild(mat)
base_link.appendChild(visual)

robot.appendChild(base_link)

#motor positions
positions = [
    [0.2, 0.2, 0],   #m0
    [0.2, -0.2, 0],   #m1
    [-0.2, 0.2, 0], #m2
    [-0.2, -0.2, 0]    #m3
]

# MOTORS LOOP
for i, pos in enumerate(positions):
    # MOTOR LINK
    motor = doc.createElement('link')
    motor.setAttribute('name', f'motor{i}')
    #addin min weight
    m_inertial = doc.createElement('inertial')
    m_mass = doc.createElement('mass')
    m_mass.setAttribute('value', '0.3') #3  30g motor
    m_inertial.appendChild(m_mass)

    m_inertia = doc.createElement('inertia')
    for attr in ['ixx', 'iyy', 'izz']:
        m_inertia.setAttribute(attr, '0.001')
    for attr in ['ixy', 'ixz', 'iyz']:
        m_inertia.setAttribute(attr, '0')
    m_inertial.appendChild(m_inertia)
    motor.appendChild(m_inertial)

    robot.appendChild(motor)

    joint = doc.createElement('joint')
    joint.setAttribute('name', f'joint{i}')
    joint.setAttribute('type', 'fixed') 

    parent = doc.createElement('parent')
    parent.setAttribute('link','base_link')
    joint.appendChild(parent)

    child = doc.createElement('child')
    child.setAttribute('link', f'motor{i}')
    joint.appendChild(child)
    
    #this is where motor is mounted (from the list)
    origin = doc.createElement('origin')
    origin.setAttribute('xyz', f"{pos[0]} {pos[1]} {pos[2]}")
    joint.appendChild(origin)

    robot.appendChild(joint)

#generating in simulation
with open("simple_drone.urdf", "w") as f:
    f.write(doc.toprettyxml(indent=" "))
print("Model simple_drone.urdf has been succesfully generated!")
