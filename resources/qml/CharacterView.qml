import QtQuick
import QtQuick.Controls
import QtQuick3D

View3D {
    id: root
    anchors.fill: parent
    camera: cam

    // Exposed property for Python to set the GLB source
    property url modelSource: ""

    environment: SceneEnvironment {
        // Use a solid background so we can see something even if the model is tiny
        backgroundMode: SceneEnvironment.Color
        clearColor: "#2e2e2e"
        antialiasingMode: SceneEnvironment.MSAA
        antialiasingQuality: SceneEnvironment.High
        // Keep defaults for tone mapping/exposure for broader compatibility
    }

    Node { id: sceneRoot }

    PerspectiveCamera {
        id: cam
        position: Qt.vector3d(0, 0, 600)
        eulerRotation: Qt.vector3d(0, 0, 0)
        clipNear: 1
        clipFar: 5000
    }
    DirectionalLight { eulerRotation: Qt.vector3d(-30, -30, 0); brightness: 2.0 }
    DirectionalLight { eulerRotation: Qt.vector3d(30, 30, 0); brightness: 1.5 }

    // Built-in primitive fallback so we always see something
    Model {
        id: fallbackCube
        objectName: "fallbackCube"
        source: "#Cube"
        parent: sceneRoot
        visible: (modelLoader.status !== Loader3D.Ready)
        scale: Qt.vector3d(400, 400, 400)
        position: Qt.vector3d(0, 0, 0)
        materials: DefaultMaterial { diffuseColor: "#ff8844" }
    }

    // Load glTF/GLB via Loader3D (supports glTF2)
    Loader3D {
        id: modelLoader
        objectName: "character"
        source: root.modelSource
        parent: sceneRoot
        visible: (status === Loader3D.Ready)
        scale: Qt.vector3d(1, 1, 1)
        position: Qt.vector3d(0, 0, 0)
        onStatusChanged: {
            // 0 Null, 1 Ready, 2 Loading, 3 Error
            if (status === Loader3D.Error) {
                console.warn("Loader3D error:", source)
            } else if (status === Loader3D.Ready) {
                console.log("Loader3D ready:", source)
            }
        }
    }
}


