"""This module provides a simple wrapper for a velocity-controlled robot."""
import numpy as np
import pybullet as pyb

from .named_tuples import getJointInfo


class Robot:
    """Wrapper for a PyBullet robot.

    Parameters
    ----------
    uid : int
        The UID of the body representing the robot.
    tool_joint_name :
        If supplied, use the child link of this joint as the end effector. If
        it is ``None``, then the link corresponding to the last joint is used.
    """

    def __init__(self, uid, tool_joint_name=None):
        self.uid = uid
        self.num_joints = pyb.getNumJoints(uid)
        self._joint_indices = list(range(self.num_joints))

        if tool_joint_name is None:
            self.tool_idx = self._joint_indices[-1]
        else:
            self.tool_idx = None
            for i in range(self.num_joints):
                info = getJointInfo(self.uid, i, decode="utf-8")
                if info.jointName == tool_joint_name:
                    self.tool_idx = info.jointIndex
                    break
            if self.tool_idx is None:
                raise ValueError(f"No joint with name {tool_joint_name} found.")

    def get_joint_states(self):
        """Get position and velocity of the robot's joints.

        Returns
        -------
        :
            A tuple ``(q, v)`` where ``q`` is the robot's joint configuration
            and ``v`` is the joint velocity.
        """
        states = pyb.getJointStates(self.uid, self._joint_indices)
        q = np.array([state[0] for state in states])
        v = np.array([state[1] for state in states])
        return q, v

    def reset_joint_configuration(self, q):
        """Reset the robot to a particular configuration.

        It is best not to do this during a simulation, as it overrides all
        dynamic effects.

        Parameters
        ----------
        q : iterable
            The vector of joint values to set. Must be of length
            ``self.num_joints``.
        """
        for idx, angle in zip(self._joint_indices, q):
            pyb.resetJointState(self.uid, idx, angle)

    def command_velocity(self, u):
        """Send a joint velocity command to the robot.

        Parameters
        ----------
        u : iterable
            The joint velocity to command. Must be of length
            ``self.num_joints``.
        """
        pyb.setJointMotorControlArray(
            self.uid,
            self._joint_indices,
            controlMode=pyb.VELOCITY_CONTROL,
            targetVelocities=list(u),
        )

    def get_link_pose(self, link_idx=None):
        """Get the pose of a link.

        The pose is computed about the link's CoM with respect to the world
        frame.

        Parameters
        ----------
        link_idx :
            Index of the link to use. If not provided, defaults to the end
            effector ``self.tool_idx``.

        Returns
        -------
        :
            A tuple containing the position and orientation quaternion of the
            link's center of mass in the world frame. The quaternion is
            represented in xyzw order.
        """
        if link_idx is None:
            link_idx = self.tool_idx
        state = pyb.getLinkState(self.uid, link_idx, computeForwardKinematics=True)
        pos, orn = state[4], state[5]
        return np.array(pos), np.array(orn)

    def get_link_velocity(self, link_idx=None):
        """Get the velocity of a link.

        The velocity is computed about the link's CoM with respect to the world
        frame.

        Parameters
        ----------
        link_idx :
            Index of the link to use. If not provided, defaults to the end
            effector ``self.tool_idx``.

        Returns
        -------
        :
            A tuple containing the linear and angular velocity vectors for the
            link's center of mass in the world frame.
        """
        if link_idx is None:
            link_idx = self.tool_idx
        state = pyb.getLinkState(
            self.uid,
            link_idx,
            computeLinkVelocity=True,
        )
        return np.array(state[-2]), np.array(state[-1])

    def jacobian(self, q=None, link_idx=None, offset=None):
        """Get the Jacobian of a point on a link at the given configuration.

        Warning
        -------
        The Jacobian is computed around the link's parent joint position,
        whereas ``get_link_pose`` and ``get_link_velocity`` compute the pose
        and velocity around the link's center of mass (CoM). To compute the
        Jacobian around the CoM, pass in the ``offset`` of the CoM from the
        joint position in the local frame. Alternatively, it may be convenient
        to simply design your URDF so that the CoM of the link of interest
        coincides with the joint origin.

        See also
        https://github.com/bulletphysics/bullet3/issues/2429#issuecomment-538431246.

        Parameters
        ----------
        q :
            The joint configuration at which to compute the Jacobian. If no
            configuration is given, then the current one is used.
        link_idx :
            The index of the link to compute the Jacobian for. The end effector
            link ``self.tool_idx`` is used if not given.
        offset :
            Offset from the parent joint position at which to compute the
            Jacobian. Defaults to zero (no offset).

        Returns
        -------
        :
            The :math:`6\\times n` Jacobian matrix, where :math:`n` is the
            number of joints.
        """

        if q is None:
            q, _ = self.get_joint_states()
        if offset is None:
            offset = np.zeros(3)
        if link_idx is None:
            link_idx = self.tool_idx

        z = list(np.zeros_like(q))
        q = list(q)
        offset = list(offset)

        Jv, Jw = pyb.calculateJacobian(self.uid, link_idx, offset, q, z, z)
        J = np.vstack((Jv, Jw))
        return J
