from pickit.Datatypes import *
from pickit.ArmManager import ArmManager
from pickit.DebraArm import DebraArm


class ArmWrapper(object):
    "Wrapper for arms"

    def __init__(self, q0, flip):
        if flip == 'right':
            flip_x = FLIP_RIGHT_HAND
            origin = Vector3D(0.15, 0.0, 0.0)
            ws_side = Workspace(0.1, 2.0, -1.0, 1.0, 0.0, 0.2, 1)
        elif flip == 'left':
            flip_x = FLIP_LEFT_HAND
            origin = Vector3D(-0.15, 0.0, 0.0)
            ws_side = Workspace(-2.0, -0.1, -1.0, 1.0, 0.0, 0.2, 1)

        arm = DebraArm(
            l1=0.2,
            l2=0.1,
            theta1_constraints=JointMinMaxConstraint(-pi / 2, pi / 2, -2, 2, -
                                                     1, 1),
            theta2_constraints=JointMinMaxConstraint(-pi / 2, pi / 2, -2, 2, -
                                                     1, 1),
            theta3_constraints=JointMinMaxConstraint(-pi / 2, pi / 2, -2, 2, -
                                                     1, 1),
            z_constraints=JointMinMaxConstraint(0, 0.2, -1, 1, -1, 1),
            q0=q0,
            origin=origin,
            flip_x=flip_x)

        ws_front = Workspace(-1.0, 1.0, 0.1, 2.0, 0.0, 0.2, 1)
        ws_back = Workspace(-1.0, 1.0, -2.0, -0.1, 0.0, 0.2, -1)
        delta_t = 0.01

        self.arm = ArmManager(arm, ws_front, ws_side, ws_back, delta_t)

    def goto(self, start, target):
        """
        Generic wrapper to move the arm
        """
        start_pos = self.arm.arm.forward_kinematics(start[0])
        self.arm.arm.compute_jacobian()
        start_vel = self.arm.arm.get_tool_vel(start[1])

        target_pos = target[0]
        target_vel = target[1]

        th1, th2, z, th3 = self.arm.goto(start_pos, start_vel, target_pos,
                                         target_vel)
        return arm_to_joint_traj(th1, th2, z, th3, self.arm.dt)


def joint_states_to_arm(z, shoulder, elbow, wrist):
    (z_pos, z_vel, z_acc, z_trq) = z
    (th1_pos, th1_vel, th1_acc, th1_trq) = shoulder
    (th2_pos, th2_vel, th2_acc, th2_trq) = elbow
    (th3_pos, th3_vel, th3_acc, th3_trq) = wrist

    pos = JointSpacePoint(th1_pos, th2_pos, z_pos, th3_pos)
    vel = JointSpacePoint(th1_vel, th2_vel, z_vel, th3_vel)

    return (pos, vel)


def arm_to_joint_traj(traj_th1, traj_th2, traj_z, traj_th3, delta_t):
    points_z = []
    points_shoulder = []
    points_elbow = []
    points_wrist = []

    for pz, pth1, pth2, pth3 in zip(traj_z, traj_th1, traj_th2, traj_th3):
        points_z.append((pz[1], pz[2], pz[3], 0))
        points_shoulder.append((pth1[1], pth1[2], pth1[3], 0))
        points_elbow.append((pth2[1], pth2[2], pth2[3], 0))
        points_wrist.append((pth3[1], pth3[2], pth3[3], 0))

    return points_z, points_shoulder, points_elbow, points_wrist
