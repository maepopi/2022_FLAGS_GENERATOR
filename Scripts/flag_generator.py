bl_info = {
    "name": "Flag Creator",
    "blender" : (3,0,0),
    "category": "Object",
    "location" : "View 3D",
    "description" : "Addon which generates and exports 3d flags",
    "author" : "Dr. Jusseaux <maelys.jusseaux@gmail.com>",
    "version":(1,0)
}

import pathlib
import os
from pydoc import visiblename
import bpy

# OPERATORS
class GENERATE_OT_generate_flags(bpy.types.Operator):
    bl_idname = "generate.generate_flags"
    bl_label = "Generate Flags"

    def execute(self,context):
        # Setup the main scene
        main_scene = bpy.context.scene
        main_scene.name = "Main Scene"
        flag_model = bpy.data.objects["Base_Flag"]

        # Clean any potential orphan images
        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)

        
        SetupRenderSettings(main_scene)


        # Declare Resources path
        textures_folder = context.scene.textures_path
        output_path = context.scene.output_path
        texture = None

        # For each item in textures_folder:
        for item in textures_folder:
            item = texture

            # Load and apply texture
            PlugTexture(main_scene, texture, flag_model)


            # Renders according to viewport camera position
            RenderFlag()

            # Renames the thumbnail
            RenameThumbnail(output_path)

            # Exports GLB
            ExportGLB(output_path)