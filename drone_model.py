from xml.dom import minidom

doc = minidom.Document()
robot = doc.createElement('robot')
robot.setAttribute('name', 'drone')
doc.appendChild(robot)

# rama
link = doc.createElement('link')
link.setAttribute('name','base_link')
link.appedCHild(link)
visual = doc.createElement('visual')
link.appendChild(visual)

#geometry
geom = doc.createElement('geometry')
box = doc.createElement('box')
box.setAttribute('size', '0.4 0.4 0.05')
geom.appendChild(box)
visual.appendChild(geom)

#material 
material = doc.createElement('material1')
material.setAttribute('name', 'dark_grey')
color = doc.createElement('color')
color.setAttribute('rgba', '0.2 0.2 0.2 1.0')
material.appendChild(color)
visual.appendChild(material)

#motors
for i in range(4):
    motor = doc.createElement('link')
    motor.setAttribute('name',f'motor{i}')
    robot.appendChild(motor)

    joint = doc.createElement('joint')

#motor positions
positions = [
    [0.2, 0.2, 0],   #m0
    [0.2, 0.0, 0],   #m1
    [-0.2, -0.2, 0], #m2
    [0.2, 0.2, 0]    #m3
]

#visualization of a motor
m_visual = doc.createElement('visual')
m_geom = doc.createElement('geometry')

#cylinder
cyl = doc.createElement('cylinder')
cyl.setAttribute('radius','0.02')
cyl.setAttribute('length','0.05')
m_geom.appendChild(cyl)
m_visual.appendChild(m_geom)

#motor color
m_mat = doc.createElement('material')
m_mat.setAttribute('name', 'red')
m_color = doc.createElement('color')
m_color.setAttribute('rgba','1. 0.0 0.0 1.0')
m_mat.appendChild(m_mat)
motor.appendChild(m_visual)

#motor connection to arm
joint = doc.createElement('joint')
joint.setAttribute('name', 'base_to_motor0')
joint.setAttribute('type', 'fixed')

#parent
parent = doc.createElement('parent')
parent.setAttribute('link', 'base link')
child = doc.createElement('child')
child.setAttribute('link', 'motor0')

#mount position
origin = doc.createAttribute('origin')
origin.setAttribute('xyz','0.2 0.2 0.0')

joint.appendChild(parent)
joint.appendChild(child)
joint.appendChild(origin)
robot.appendChild(joint)