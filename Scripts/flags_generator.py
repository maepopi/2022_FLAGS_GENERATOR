bl_info = {
    "name": "Flag Generator",
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

# OPERATOR
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

        
        return{'FINISHED'}


# PANEL
class VIEW3D_PT_generate_flags(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Flag Generator"
    bl_label = "Generate"

    def draw(self, context):
        layout = self.layout

        # Path to texture folder
        row = layout.row()
        col = row.column()
        col.prop(context.scene, "texture_path")

        # Output path
        col = layout.column()
        col.prop(context.scene, "output_path")

        # Generate
        col = layout.column()
        col.operator("generate.generate_flags")

        
        




# REGISTER AND UNREGISTER CLASSES
classes = [
    GENERATE_OT_generate_flags,
    VIEW3D_PT_generate_flags
]

def register():
    bpy.types.Scene.texture_path = bpy.props.StringProperty(
        name = 'Textures Folder',
        subtype = 'DIR_PATH',
    )

    bpy.types.Scene.output_path = bpy.props.StringProperty(
    name='Output Folder',
    subtype='DIR_PATH',
    )

    for c in classes:
        bpy.utils.register_class(c)



def unregister():
    del bpy.types.Scene.texture_path
    del bpy.types.Scene.output_path

    for c in classes:
        bpy.utils.unregister_class(c)

