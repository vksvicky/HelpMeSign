"""
Model loading and management for AnimateGesturePanel.
Handles 3D model loading, camera setup, lighting, and joint management.
"""

from typing import Any, Dict, List, Optional

from ....utils.joint_constraints import joint_validator
from ....utils.logger import get_logger


class ModelManager:
    """Manages 3D model loading and setup for AnimateGesturePanel"""

    def __init__(self, parent_panel):
        self.parent_panel = parent_panel
        self._log = get_logger("helpmesign.modes.learn.animate_panel.model")

    def load_model_internal(self, model_path: str) -> None:
        """Load a 3D model from the given path."""
        try:
            if not self.parent_panel._panda_ready:
                return

            # Load the model
            from panda3d.core import Filename, NodePath  # type: ignore[attr-defined]

            # Convert to absolute path if needed
            if not model_path.startswith("/"):
                import os

                model_path = os.path.abspath(model_path)

            self._log.info(f"Loading 3D model: {model_path}")

            # Load the model file
            model_node = self.parent_panel._showbase.loader.loadModel(
                Filename(model_path)
            )
            if not model_node:
                self._log.error(f"Failed to load model: {model_path}")
                return

            # Clear existing model
            if hasattr(self.parent_panel, "_model_np") and self.parent_panel._model_np:
                self.parent_panel._model_np.removeNode()

            # Create Actor for skeletal control
            try:
                from direct.actor.Actor import Actor

                self.parent_panel._actor = Actor(model_node, {})
                self.parent_panel._model_np = self.parent_panel._actor
                self._log.info("Loaded model as Actor for skeletal control")
            except Exception:
                # Fallback to regular NodePath
                self.parent_panel._model_np = NodePath(model_node)
                self.parent_panel._actor = None
                self._log.info("Loaded model as regular NodePath")

            # Add to scene
            self.parent_panel._model_np.reparentTo(self.parent_panel._scene)

            # Apply default pose and camera setup
            self._apply_default_neutral_pose()
            self._set_camera_for_default_pose()
            self._setup_lighting()

            # Frame the model in view
            self._frame_model(self.parent_panel._model_np)

        except Exception as e:
            self._log.error(f"Error loading model: {e}")

    def _apply_default_neutral_pose(self):
        """Apply default neutral pose to the model."""
        try:
            if not self.parent_panel._model_np:
                return

            # Try to apply idle pose if it's an Actor
            if self.parent_panel._actor:
                try:
                    self.parent_panel._actor.pose("idle", 0)
                    self._log.info("Applied idle pose to Actor")
                except Exception:
                    self._log.info(
                        "Using character's natural model pose - no joint modifications applied"
                    )

            # Set default position and orientation
            self.parent_panel._model_np.setPos(0, 0, 0)
            self.parent_panel._model_np.setHpr(0, 0, 0)
            self.parent_panel._model_np.setScale(1, 1, 1)

        except Exception as e:
            self._log.error(f"Error applying default pose: {e}")

    def _set_camera_for_default_pose(self) -> None:
        """Set camera position for optimal viewing of the default pose."""
        try:
            if not self.parent_panel._camera or not self.parent_panel._model_np:
                return

            # Position camera for front-facing T-pose view
            self.parent_panel._camera.setPos(
                0, -5, 1.5
            )  # Back, up, and slightly elevated
            self.parent_panel._camera.lookAt(self.parent_panel._model_np)

            self._log.info("Camera positioned for front-facing T-pose view")

        except Exception as e:
            self._log.error(f"Error setting camera position: {e}")

    def _setup_lighting(self):
        """Setup lighting for the scene."""
        try:
            if not self.parent_panel._showbase:
                return

            # Create ambient light
            from panda3d.core import (
                AmbientLight,
                DirectionalLight,
                PointLight,
            )

            # Ambient light for overall illumination
            ambient_light = AmbientLight("ambient")
            ambient_light.setColor((0.3, 0.3, 0.3, 1))
            ambient_np = self.parent_panel._showbase.render.attachNewNode(ambient_light)
            self.parent_panel._showbase.render.setLight(ambient_np)

            # Main directional light
            directional_light = DirectionalLight("directional")
            directional_light.setColor((0.8, 0.8, 0.8, 1))
            directional_np = self.parent_panel._showbase.render.attachNewNode(
                directional_light
            )
            directional_np.setHpr(45, -45, 0)
            self.parent_panel._showbase.render.setLight(directional_np)

            # Fill light from the opposite side
            fill_light = DirectionalLight("fill")
            fill_light.setColor((0.4, 0.4, 0.4, 1))
            fill_np = self.parent_panel._showbase.render.attachNewNode(fill_light)
            fill_np.setHpr(-45, -45, 0)
            self.parent_panel._showbase.render.setLight(fill_np)

        except Exception as e:
            self._log.error(f"Error setting up lighting: {e}")

    def _frame_model(self, node, fill_fraction: float = 0.75) -> None:
        """Frame the model in the camera view."""
        try:
            import math

            from panda3d.core import Point3

            # Compute tight bounds in model space
            min_pt, max_pt = node.getTightBounds()
            if not min_pt or not max_pt:
                # Fallback: simple placement
                node.setPos(0, 3.0, 0)
                node.setScale(1.5)
                self.parent_panel._camera.setPos(0, -6.0, 1.5)
                self.parent_panel._camera.lookAt(node)
                return

            size = max_pt - min_pt
            center = (min_pt + max_pt) * 0.5

            # Move model so its center is at the origin
            node.setPos(-center.x, -center.y, -center.z)

            # Use bounding sphere radius to compute distance
            radius = max(1e-3, max(size.x, size.y, size.z) * 0.5)
            lens = self.parent_panel._showbase.camLens
            fov_v_deg = 40.0
            try:
                fov = lens.getFov()
                if len(fov) == 2:
                    fov_v_deg = float(fov[1])
            except Exception:
                pass
            fov_v = math.radians(max(1.0, fov_v_deg))
            distance = (radius / math.tan(fov_v * 0.5)) / max(
                0.2, min(0.95, fill_fraction)
            )
            distance = distance * 1.2  # Reduced back-off to make character larger

            # Place camera for full body view when not signing
            # Position camera to show full character with arms in front
            self.parent_panel._camera.setPos(
                0, -distance, radius * 0.2
            )  # Full body view - moved up
            self.parent_panel._camera.lookAt(
                0, 0, radius * 0.2
            )  # Look at character's center - moved up

            # Keep neutral scaling
            node.setScale(1.0)
        except Exception:
            # Non-fatal framing issues should not break the panel
            try:
                node.setPos(0, 3.0, 0)
                node.setScale(1.5)
                self.parent_panel._camera.setPos(0, -6.0, 1.5)
                self.parent_panel._camera.lookAt(node)
            except Exception:
                pass

    def _find_node_by_names(self, names) -> Optional[Any]:
        """Find a node by trying multiple possible names."""
        try:
            if not self.parent_panel._model_np:
                return None

            for name in names:
                try:
                    node = self.parent_panel._model_np.find(f"**/{name}")
                    if node and not node.isEmpty():
                        return node
                except Exception:
                    continue

            return None

        except Exception as e:
            self._log.error(f"Error finding node by names: {e}")
            return None

    def _get_joint_node(self, name: str) -> Optional[Any]:
        """Get a joint node by name with fallback aliases."""
        try:
            if not self.parent_panel._model_np:
                return None

            # Try exact name first
            joint_node = self.parent_panel._model_np.find(f"**/{name}")
            if joint_node and not joint_node.isEmpty():
                return joint_node

            # Try with best alias
            best_alias = self._best_alias(name)
            if best_alias != name:
                joint_node = self.parent_panel._model_np.find(f"**/{best_alias}")
                if joint_node and not joint_node.isEmpty():
                    return joint_node

            return None

        except Exception as e:
            self._log.error(f"Error getting joint node {name}: {e}")
            return None

    def _best_alias(self, name: str) -> str:
        """Get the best alias for a joint name."""
        try:
            # Common joint name mappings
            aliases = {
                "RightHand": ["RightHand", "right_hand", "hand.R", "Right_Hand"],
                "LeftHand": ["LeftHand", "left_hand", "hand.L", "Left_Hand"],
                "RightArm": ["RightArm", "right_arm", "arm.R", "Right_Arm"],
                "LeftArm": ["LeftArm", "left_arm", "arm.L", "Left_Arm"],
                "RightShoulder": [
                    "RightShoulder",
                    "right_shoulder",
                    "shoulder.R",
                    "Right_Shoulder",
                ],
                "LeftShoulder": [
                    "LeftShoulder",
                    "left_shoulder",
                    "shoulder.L",
                    "Left_Shoulder",
                ],
                "RightElbow": ["RightElbow", "right_elbow", "elbow.R", "Right_Elbow"],
                "LeftElbow": ["LeftElbow", "left_elbow", "elbow.L", "Left_Elbow"],
                "RightWrist": ["RightWrist", "right_wrist", "wrist.R", "Right_Wrist"],
                "LeftWrist": ["LeftWrist", "left_wrist", "wrist.L", "Left_Wrist"],
                "RightFinger": [
                    "RightFinger",
                    "right_finger",
                    "finger.R",
                    "Right_Finger",
                ],
                "LeftFinger": ["LeftFinger", "left_finger", "finger.L", "Left_Finger"],
            }

            # Check if we have aliases for this joint
            if name in aliases:
                for alias in aliases[name]:
                    try:
                        node = self.parent_panel._model_np.find(f"**/{alias}")
                        if node and not node.isEmpty():
                            return alias
                    except Exception:
                        continue

            # Return original name if no alias found
            return name

        except Exception as e:
            self._log.error(f"Error finding best alias for {name}: {e}")
            return name

    def _dump_node_names(self) -> None:
        """Dump all node names for debugging."""
        try:
            if not self.parent_panel._model_np:
                return

            def print_nodes(node, indent=0):
                print("  " * indent + node.getName())
                for child in node.getChildren():
                    print_nodes(child, indent + 1)

            print("Model node hierarchy:")
            print_nodes(self.parent_panel._model_np)

        except Exception as e:
            self._log.error(f"Error dumping node names: {e}")

    def _apply_fallback_movement(self) -> None:
        """Apply fallback movement when pose validation fails."""
        try:
            if not self.parent_panel._actor:
                return

            # Simple fallback: slight rotation
            self.parent_panel._model_np.setH(self.parent_panel._model_np.getH() + 5)

        except Exception as e:
            self._log.error(f"Error applying fallback movement: {e}")

    def validate_pose_before_application(self, pose: Dict[str, List[float]]) -> bool:
        """Validate pose data before applying it."""
        try:
            if not pose:
                return False

            # Check if pose is anatomically valid
            return self.is_pose_anatomically_valid(pose)

        except Exception as e:
            self._log.error(f"Error validating pose: {e}")
            return False

    def is_pose_anatomically_valid(self, pose: Dict[str, List[float]]) -> bool:
        """Check if pose is anatomically valid using joint constraints."""
        try:
            if not pose:
                return False

            # Use joint validator to check constraints
            for joint_name, rotation_data in pose.items():
                if len(rotation_data) >= 3:
                    constraint_info = self.get_joint_constraint_info(joint_name)
                    if constraint_info:
                        # Validate rotation against constraints
                        if not joint_validator.is_rotation_valid(  # type: ignore[attr-defined]
                            rotation_data, constraint_info
                        ):
                            return False

            return True

        except Exception as e:
            self._log.error(f"Error checking pose validity: {e}")
            return False

    def get_joint_constraint_info(self, joint_name: str) -> Optional[Dict]:
        """Get constraint information for a joint."""
        try:
            # This would typically come from a joint constraints configuration
            # For now, return None to skip validation
            return None

        except Exception as e:
            self._log.error(f"Error getting joint constraint info: {e}")
            return None
