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

                # Debug: Check if the model has the required structure for Actor
                self._log.info(f"Model node type: {type(model_node)}")
                self._log.info(f"Model node name: {model_node.getName()}")

                # Try to create Actor
                self.parent_panel._actor = Actor(model_node, {})
                self.parent_panel._model_np = self.parent_panel._actor
                self._log.info("Loaded model as Actor for skeletal control")

                # Debug: Check if Actor was created successfully
                if self.parent_panel._actor:
                    self._log.info("Actor created successfully")
                    # Try to get joint information
                    try:
                        joints = self.parent_panel._actor.getJoints()
                        self._log.info(f"Found {len(joints)} joints in the model")
                        if joints:
                            self._log.info(f"First few joints: {joints[:5]}")
                    except Exception as e:
                        self._log.warning(f"Could not get joints from Actor: {e}")
                else:
                    self._log.warning("Actor creation returned None")

            except Exception as e:
                self._log.warning(f"Failed to create Actor: {e}")
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

            # Set enhanced visibility color for better hand gesture visibility
            self._set_enhanced_visibility_color()

            # Set joint colors to black for better visibility
            self._set_joint_colors()

            # Frame the model in view
            self._frame_model(self.parent_panel._model_np)

        except Exception as e:
            self._log.error(f"Error loading model: {e}")

    def _apply_default_neutral_pose(self):
        """Apply default neutral pose to the model."""
        try:
            if not self.parent_panel._model_np:
                return

            # Use the hands-down pose from the GLB file as the default neutral pose
            if self.parent_panel._actor:
                try:
                    # Stop any current animations
                    self.parent_panel._actor.stop()

                    # Apply the hands-down pose (first animation frame 0)
                    # This is the natural pose with arms by the sides
                    self.parent_panel._actor.pose("Armature|mixamo.com|Layer0", 0)
                    self._log.info("Applied hands-down pose as default neutral pose")

                except Exception as e:
                    self._log.warning(f"Could not apply hands-down pose: {e}")
                    # Fallback to bind pose if animation fails
                    try:
                        self.parent_panel._actor.pose("", 0)
                        self._log.info("Fallback to bind pose")
                    except Exception as fallback_error:
                        self._log.warning(
                            f"Could not apply bind pose either: {fallback_error}"
                        )

            # Set default position and orientation
            self.parent_panel._model_np.setPos(0, 0, 0)
            self.parent_panel._model_np.setHpr(0, 0, 0)
            self.parent_panel._model_np.setScale(1, 1, 1)

        except Exception as e:
            self._log.error(f"Error applying default pose: {e}")

    def _set_enhanced_visibility_color(self) -> None:
        """Set enhanced visibility color for better hand gesture visibility."""
        try:
            if not self.parent_panel._model_np:
                return

            from panda3d.core import VBase4

            # Set default blue color for better visibility
            enhanced_color = VBase4(0.1, 0.3, 0.9, 1.0)  # High contrast blue
            self.parent_panel._model_np.setColor(enhanced_color)
            self._log.info(
                "Applied enhanced visibility color for better hand gesture visibility"
            )

        except Exception as e:
            self._log.error(f"Error setting enhanced visibility color: {e}")

    def _set_joint_colors(self) -> None:
        """Set joint colors to black for better visibility."""
        try:
            if not self.parent_panel._model_np:
                return

            from panda3d.core import VBase4

            black_color = VBase4(0.0, 0.0, 0.0, 1.0)  # Black
            colored_geometry = 0

            # Method 1: Color all geometry nodes that might be joints
            print("=== Method 1: Coloring all geometry nodes ===")
            geom_nodes = self.parent_panel._model_np.findAllMatches("**/+GeomNode")
            for i in range(geom_nodes.getNumPaths()):
                geom_node = geom_nodes.getPath(i)
                try:
                    # Check if this geometry is small (likely a joint)
                    bounds = geom_node.getBounds()
                    if bounds:
                        size = bounds.getSize()
                        if size.length() < 0.2:  # Small geometry threshold
                            geom_node.setColor(black_color)
                            colored_geometry += 1
                            print(f"  ✓ Colored small geometry: {geom_node.getName()}")
                except Exception as e:
                    print(f"  ✗ Could not color geometry {i}: {e}")

            # Method 2: Try to find and color joint-related geometry by name patterns
            print("=== Method 2: Coloring joint-related geometry ===")
            joint_patterns = [
                "**/*joint*",
                "**/*Joint*",
                "**/*bone*",
                "**/*Bone*",
                "**/*skeleton*",
                "**/*Skeleton*",
            ]

            for pattern in joint_patterns:
                try:
                    nodes = self.parent_panel._model_np.findAllMatches(pattern)
                    for j in range(nodes.getNumPaths()):
                        node = nodes.getPath(j)
                        try:
                            node.setColor(black_color)
                            colored_geometry += 1
                            print(f"  ✓ Colored {pattern} node: {node.getName()}")
                        except Exception as e:
                            print(f"  ✗ Could not color {node.getName()}: {e}")
                except Exception as e:
                    print(f"  ✗ Pattern {pattern} failed: {e}")

            # Method 3: Color specific body parts that might be joints
            print("=== Method 3: Coloring specific body parts ===")
            body_parts = ["Head", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle"]
            for part in body_parts:
                try:
                    part_nodes = self.parent_panel._model_np.findAllMatches(
                        f"**/*{part}*"
                    )
                    for k in range(part_nodes.getNumPaths()):
                        part_node = part_nodes.getPath(k)
                        try:
                            part_node.setColor(black_color)
                            colored_geometry += 1
                            print(f"  ✓ Colored {part} part: {part_node.getName()}")
                        except Exception as e:
                            print(f"  ✗ Could not color {part_node.getName()}: {e}")
                except Exception as e:
                    print(f"  ✗ Error with {part}: {e}")

            print(f"=== Total colored geometry: {colored_geometry} ===")
            self._log.info(f"Set {colored_geometry} geometry nodes to black color")

        except Exception as e:
            self._log.error(f"Error setting joint colors: {e}")

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

            # Get current theme to adjust lighting accordingly
            current_theme = self._get_current_theme()

            # Create ambient light
            from panda3d.core import (
                AmbientLight,
                DirectionalLight,
            )

            # Theme-aware ambient lighting with maximum visibility for hand gestures
            if current_theme == "Light":
                # Maximum lighting for Light theme to provide optimal hand gesture visibility
                ambient_intensity = (
                    0.6  # Further increased ambient for maximum visibility
                )
                directional_intensity = (
                    1.6  # Maximum directional for strongest shadows and definition
                )
                fill_intensity = 1.2  # Maximum fill light for optimal hand definition
            else:
                # Enhanced lighting for Dark theme to maximize hand gesture visibility
                ambient_intensity = 0.5  # Increased ambient for better visibility
                directional_intensity = (
                    1.2  # Increased directional for better definition
                )
                fill_intensity = 0.8  # Increased fill light for better hand visibility

            # Ambient light for overall illumination
            ambient_light = AmbientLight("ambient")
            ambient_light.setColor(
                (ambient_intensity, ambient_intensity, ambient_intensity, 1)
            )
            ambient_np = self.parent_panel._showbase.render.attachNewNode(ambient_light)
            self.parent_panel._showbase.render.setLight(ambient_np)

            # Main directional light
            directional_light = DirectionalLight("directional")
            directional_light.setColor(
                (directional_intensity, directional_intensity, directional_intensity, 1)
            )
            directional_np = self.parent_panel._showbase.render.attachNewNode(
                directional_light
            )
            directional_np.setHpr(45, -45, 0)
            self.parent_panel._showbase.render.setLight(directional_np)

            # Fill light from the opposite side
            fill_light = DirectionalLight("fill")
            fill_light.setColor((fill_intensity, fill_intensity, fill_intensity, 1))
            fill_np = self.parent_panel._showbase.render.attachNewNode(fill_light)
            fill_np.setHpr(-45, -45, 0)
            self.parent_panel._showbase.render.setLight(fill_np)

        except Exception as e:
            self._log.error(f"Error setting up lighting: {e}")

    def _adjust_model_materials_for_theme(self) -> None:
        """Adjust model materials for better visibility in the current theme."""
        try:
            if not self.parent_panel._model_np:
                return

            current_theme = self._get_current_theme()

            if current_theme == "Light":
                # In light mode, don't change the character - just use default materials
                # The lighting improvements will provide better visibility
                self._log.info(
                    "Using default materials for Light theme - lighting provides contrast"
                )
            else:
                # In dark mode, use default materials
                if hasattr(self.parent_panel._model_np, "clearMaterial"):
                    self.parent_panel._model_np.clearMaterial(1)
                    self._log.info("Cleared material for Dark theme")

        except Exception as e:
            self._log.error(f"Error adjusting model materials for theme: {e}")

    def _get_current_theme(self) -> str:
        """Get the current application theme."""
        try:
            # Use the global theme manager instead of loading configuration
            from ....utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager()
            return theme_manager.get_current_theme()
        except Exception:
            # Fallback to default Light theme
            return "Light"

    def _frame_model(self, node, fill_fraction: float = 0.75) -> None:
        """Frame the model in the camera view."""
        try:
            import math

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
