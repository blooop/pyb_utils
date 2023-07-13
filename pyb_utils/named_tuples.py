from collections import namedtuple

import pybullet as pyb


# field names are camel case to match bullet convention
DynamicsInfo = namedtuple(
    "DynamicsInfo",
    [
        "mass",
        "lateralFriction",
        "localInertiaDiagonal",
        "localInerialPos",
        "localInertialOrn",
        "restitution",
        "rollingFriction",
        "spinningFriction",
        "contactDamping",
        "contactStiffness",
        "bodyType",
        "collisionMargin",
    ],
)

ContactPoint = namedtuple(
    "ContactPoint",
    [
        "contactFlag",
        "bodyUniqueIdA",
        "bodyUniqueIdB",
        "linkIndexA",
        "linkIndexB",
        "positionOnA",
        "positionOnB",
        "contactNormalOnB",
        "contactDistance",
        "normalForce",
        "lateralFriction1",
        "lateralFrictionDir1",
        "lateralFriction2",
        "lateralFrictionDir2",
    ],
)


def getDynamicsInfo(bodyUniqueId, linkIndex, physicsClientId=0):
    return DynamicsInfo(
        *pyb.getDynamicsInfo(bodyUniqueId, linkIndex, physicsClientId)
    )


def getContactPoints(
    bodyA=-1, bodyB=-1, linkIndexA=-2, linkIndexB=-2, physicsClientId=0
):
    points_raw = pyb.getContactPoints(
        bodyA, bodyB, linkIndexA, linkIndexB, physicsClientId
    )
    return [ContactPoint(*point) for point in points_raw]


def getClosestPoints(
    bodyA, bodyB, distance, linkIndexA=-2, linkIndexB=-2, physicsClientId=0
):
    points_raw = pyb.getClosestPoints(
        bodyA, bodyB, distance, linkIndexA, linkIndexB, physicsClientId
    )
    return [ContactPoint(*point) for point in points_raw]
