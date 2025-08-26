#!/usr/bin/env python3
"""
Test script to understand character joint structure and test basic joint control
"""

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData

from helpmesign.utils.resource_manager import ResourceManager


def test_character_joints():
    """Test character joint structure and basic control"""

    # Check if ShowBase already exists (from other tests)
    import builtins

    created_showbase = False
    if hasattr(builtins, "base"):
        # Use existing ShowBase instance
        base = builtins.base
    else:
        # Setup Panda3D
        loadPrcFileData("", "window-type offscreen")
        loadPrcFileData("", "sync-video 0")
        base = ShowBase(windowType="offscreen")
        created_showbase = True

    # Load character
    resource_manager = ResourceManager()
    model_path = resource_manager.get_resource_path("characters", "arivo.glb")

    print(f"Loading character from: {model_path}")

    try:
        actor = Actor(model_path)
        print("✅ Character loaded successfully as Actor")

        # Get all joints
        joints = list(actor.getJoints())
        print(f"📋 Total joints: {len(joints)}")

        # Print all joint names
        print("\n🔍 All joint names:")
        for i, joint in enumerate(joints):
            print(f"  {i+1:2d}. {joint.getName()}")

        # Test basic joint control
        print("\n🧪 Testing basic joint control:")

        # Test arm joints
        arm_joints = [
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
        ]

        for joint_name in arm_joints:
            try:
                joint = actor.controlJoint(None, "modelRoot", joint_name)
                if joint and not joint.isEmpty():
                    print(f"  ✅ {joint_name}: Found and controllable")
                    # Get current HPR
                    hpr = joint.getHpr()
                    print(f"     Current HPR: {hpr}")
                else:
                    print(f"  ❌ {joint_name}: Not found or not controllable")
            except Exception as e:
                print(f"  ❌ {joint_name}: Error - {e}")

        # Test finger joints
        print("\n👆 Testing finger joints:")
        finger_joints = [
            "mixamorig:RightHandIndex1",
            "mixamorig:RightHandIndex2",
            "mixamorig:RightHandIndex3",
            "mixamorig:RightHandMiddle1",
            "mixamorig:RightHandMiddle2",
            "mixamorig:RightHandMiddle3",
            "mixamorig:RightHandRing1",
            "mixamorig:RightHandRing2",
            "mixamorig:RightHandRing3",
            "mixamorig:RightHandPinky1",
            "mixamorig:RightHandPinky2",
            "mixamorig:RightHandPinky3",
            "mixamorig:RightHandThumb1",
            "mixamorig:RightHandThumb2",
            "mixamorig:RightHandThumb3",
            "mixamorig:LeftHandIndex1",
            "mixamorig:LeftHandIndex2",
            "mixamorig:LeftHandIndex3",
            "mixamorig:LeftHandMiddle1",
            "mixamorig:LeftHandMiddle2",
            "mixamorig:LeftHandMiddle3",
            "mixamorig:LeftHandRing1",
            "mixamorig:LeftHandRing2",
            "mixamorig:LeftHandRing3",
            "mixamorig:LeftHandPinky1",
            "mixamorig:LeftHandPinky2",
            "mixamorig:LeftHandPinky3",
            "mixamorig:LeftHandThumb1",
            "mixamorig:LeftHandThumb2",
            "mixamorig:LeftHandThumb3",
        ]

        controllable_fingers = []
        for joint_name in finger_joints:
            try:
                joint = actor.controlJoint(None, "modelRoot", joint_name)
                if joint and not joint.isEmpty():
                    controllable_fingers.append(joint_name)
                    print(f"  ✅ {joint_name}: Controllable")
                else:
                    print(f"  ❌ {joint_name}: Not controllable")
            except Exception as e:
                print(f"  ❌ {joint_name}: Error - {e}")

        print(f"\n📊 Summary:")
        print(f"  Total joints: {len(joints)}")
        print(f"  Controllable finger joints: {len(controllable_fingers)}")

        # Test a simple pose
        print("\n🎭 Testing simple pose:")
        try:
            # Test right arm movement
            right_arm = actor.controlJoint(None, "modelRoot", "mixamorig:RightArm")
            if right_arm and not right_arm.isEmpty():
                print("  Testing right arm movement...")
                right_arm.setHpr(45, 30, 0)  # Move arm forward and up
                print("  ✅ Right arm moved to H=45, P=30, R=0")

            # Test left arm movement
            left_arm = actor.controlJoint(None, "modelRoot", "mixamorig:LeftArm")
            if left_arm and not left_arm.isEmpty():
                print("  Testing left arm movement...")
                left_arm.setHpr(-45, 30, 0)  # Move arm forward and up
                print("  ✅ Left arm moved to H=-45, P=30, R=0")

        except Exception as e:
            print(f"  ❌ Error testing pose: {e}")

        print("\n✅ Joint testing completed!")

    except Exception as e:
        print(f"❌ Error loading character: {e}")

    finally:
        # Only destroy ShowBase if we created it
        if created_showbase:
            base.destroy()


if __name__ == "__main__":
    test_character_joints()
