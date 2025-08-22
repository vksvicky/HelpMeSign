#!/usr/bin/env python3
"""
Debug script to check available joints in the 3D model
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from helpmesign.utils.resource_manager import ResourceManager


def main():
    # Get the model path
    resource_manager = ResourceManager()
    model_path = resource_manager.get_model_path("arivo.glb")
    print(f"Model path: {model_path}")

    if not os.path.exists(model_path):
        print(f"Model file does not exist: {model_path}")
        return

    try:
        from direct.actor.Actor import Actor
        from direct.showbase.ShowBase import ShowBase
        from panda3d.core import loadPrcFileData

        # Initialize Panda3D
        loadPrcFileData("", "window-type offscreen")
        loadPrcFileData("", "sync-video 0")

        showbase = ShowBase(windowType="offscreen")

        # Load the model
        print("Loading model...")
        actor = Actor(model_path)
        print("Model loaded successfully!")

        # Try to get joint names
        print("\nChecking for common joint names:")
        joint_names_to_check = [
            "mixamorig:RightArm",
            "mixamorig:LeftArm",
            "mixamorig:RightHand",
            "mixamorig:LeftHand",
            "mixamorig:RightForeArm",
            "mixamorig:LeftForeArm",
            "RightArm",
            "LeftArm",
            "RightHand",
            "LeftHand",
            "hand_r",
            "hand_l",
            "arm_r",
            "arm_l",
        ]

        for joint_name in joint_names_to_check:
            try:
                joint = actor.controlJoint(None, "modelRoot", joint_name)
                if joint and not joint.isEmpty():
                    print(f"  ✓ {joint_name} - Available")
                else:
                    print(f"  ✗ {joint_name} - Not found")
            except Exception as e:
                print(f"  ✗ {joint_name} - Error: {e}")

        # Try to find all joints in the model
        print("\nSearching for all joints in the model...")
        try:
            root = actor.getParent()
            if root:
                all_nodes = root.findAllMatches("**/*")
                joint_count = 0
                for i in range(all_nodes.getNumPaths()):
                    node = all_nodes.getPath(i)
                    name = node.getName()
                    if any(
                        keyword in name.lower()
                        for keyword in ["arm", "hand", "finger", "joint"]
                    ):
                        print(f"  Found joint: {name}")
                        joint_count += 1
                        if joint_count > 20:  # Limit output
                            print("  ... (showing first 20 joints)")
                            break
            else:
                print("  Could not find root node")
        except Exception as e:
            print(f"  Error searching for joints: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
