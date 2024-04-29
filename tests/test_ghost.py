import numpy as np
import pybullet as pyb
import pyb_utils


def setup_function():
    pyb.connect(pyb.DIRECT)
    # pyb.setAdditionalSearchPath(pybullet_data.getDataPath())

    pyb.loadURDF("plane.urdf", [0, 0, 0], useFixedBase=True)


def teardown_function():
    pyb.disconnect()


def test_ghost_arrow():
    """Super basic test that arrow code doesn't crash because it can't find the model"""
    arrow = pyb_utils.GhostObject.arrow([0,0,0],[1,1,1])
    arrow.remove()
    
