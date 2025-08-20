import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, VBase4


class CharacterWindow(ShowBase):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("HelpMeSign - 3D Character")

        # Set background color
        self.setBackgroundColor(0.1, 0.1, 0.1, 1.0)

        # Enable antialiasing
        self.render.setAntialias(AntialiasAttrib.MAuto)

        # Load character
        self.load_character()

        # Setup camera
        self.setup_camera()

        # Start animation
        self.start_animation()

    def load_character(self):
        """Load the character model"""
        try:
            # Load character model
            model_path = "resources/characters/arivo.glb"
            if os.path.exists(model_path):
                self.actor = Actor(model_path)
                self.actor.reparentTo(self.render)
                self.actor.setColor(VBase4(0.8, 0.6, 0.4, 1.0))
                print("Character loaded successfully")
            else:
                print(f"Model not found: {model_path}")
        except Exception as e:
            print(f"Error loading character: {e}")

    def setup_camera(self):
        """Setup camera position"""
        self.camera.setPos(0, -5, 1)
        self.camera.lookAt(0, 0, 1)

    def start_animation(self):
        """Start the welcome animation"""
        # Simple animation - move arms up and down
        from direct.interval.IntervalGlobal import Parallel, Sequence
        from panda3d.core import Vec3

        # Get arm joints
        right_arm = self.actor.controlJoint(None, "modelRoot", "mixamorig:RightArm")
        left_arm = self.actor.controlJoint(None, "modelRoot", "mixamorig:LeftArm")

        if right_arm and left_arm:
            # Create animation sequence
            from direct.interval.IntervalGlobal import LerpHprInterval

            # Arms up
            arms_up = Parallel(
                LerpHprInterval(right_arm, 2, (90, 45, 0)),
                LerpHprInterval(left_arm, 2, (-90, 45, 0)),
            )

            # Arms down
            arms_down = Parallel(
                LerpHprInterval(right_arm, 2, (0, 0, 0)),
                LerpHprInterval(left_arm, 2, (0, 0, 0)),
            )

            # Play sequence
            Sequence(arms_up, arms_down).loop()
            print("Animation started")


if __name__ == "__main__":
    app = CharacterWindow()
    app.run()
