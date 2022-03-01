bl_info = {
    "name": "Flag Generator",
    "blender" : (3,0,0),
    "category": "Object",
    "location" : "View 3D",
    "description" : "Addon which generates and exports 3d flags",
    "author" : "Dr. Jusseaux <maelys.jusseaux@gmail.com>",
    "version":(1,0)
}

from email.mime import base
from json.tool import main
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
        base_model = bpy.data.objects["Base_Pole"]
        models = [flag_model, base_model]
        

        # Clean any potential orphan images
        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)

        
        SetupRenderSettings(main_scene)


        # Declare Resources path
        textures_folder_path = context.scene.textures_path
        output_path = context.scene.output_path
        texture_path = None
        name = None

        textures_list = os.listdir(textures_folder_path)
        

        # For each item in textures_folder:
        for item in textures_list:
            print ("Texture is " + str(item))
            texture_path = os.path.join(textures_folder_path, item)
            print ("Texture path is " + str(texture_path))
            texture_name = os.path.splitext(item)[0]
            print("Texture name is " + texture_name)


            # Load and apply texture
            PlugTexture(main_scene, texture_path)

            #Prepare compositor
            PrepareCompositor(main_scene, output_path, texture_name)

            # # Renders according to viewport camera position
            RenderFlag()

            # Renames the thumbnail
            RenameThumbnail(output_path, texture_name)

            # Exports GLB
            ExportGLB(models, output_path, texture_name)

        
        return{'FINISHED'}


# PANEL
class VIEW3D_PT_generate_flags(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Flag Generator"
    bl_label = "Generate Flags"

    def draw(self, context):
        layout = self.layout

        # Path to texture folder
        row = layout.row()
        col = row.column()
        col.prop(context.scene, "textures_path")

        # Output path
        col = layout.column()
        col.prop(context.scene, "output_path")

        # Generate
        col = layout.column()
        col.operator("generate.generate_flags")

        
        

# FUNCTIONS
def SetupRenderSettings(scene):
    #   Create and place the camera
    bpy.ops.object.camera_add(align='VIEW')
    bpy.ops.view3d.camera_to_view()

    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.film_transparent = True


def PlugTexture(scene, path):
    # Get the right material and its nodes
    # Alternative : take the first slot of the list of materials of the object
    material = bpy.data.materials["Flag_Material"]
    node_tree = material.node_tree
    links = node_tree.links

    # Get the base color
    image_node = node_tree.nodes["Image Texture"]

    # Load image in the image_node
    image = bpy.data.images.load(filepath = path)
    image_node.image = image


def PrepareCompositor(scene, path, name):
    bpy.context.area.ui_type = 'CompositorNodeTree'
    scene_tree = scene.node_tree
    links = scene_tree.links
    output_node = scene_tree.nodes["File Output"]
    output_node.base_path = path
    print("The output render path is " + str(path) )


def RenderFlag():
    bpy.ops.render.render(layer="ViewLayer", write_still=True)
    


def RenameThumbnail(path, name):
    original_folder = path

    for item in os.listdir(original_folder):
        print("rename thumbnail name " + item)
        print("rename thumbnail original folder " + str(original_folder))
        original_filepath = os.path.join(original_folder, item)

        print("rename thumbnail original filepath is " + str(original_filepath))

        if 'Image0000.png' in item:
            original_filepath = os.path.join(original_folder, item)
            original_name = os.path.splitext(item)[0]
            extension = os.path.splitext(item)[1]
            new_filepath = os.path.join(original_folder, name + "_thumbnail" + extension)
            os.rename(original_filepath, new_filepath)
        
        else:
            print("Image not found")


def ExportGLB(list, path, name):
    for item in list:
        item.select_set(True)
    
    
    extension = ".glb"
    output_path = os.path.join(path, name + extension)



    bpy.ops.export_scene.gltf(filepath=output_path, export_format="GLB", export_selected=True)














# REGISTER AND UNREGISTER CLASSES
classes = [
    GENERATE_OT_generate_flags,
    VIEW3D_PT_generate_flags
]

def register():
    bpy.types.Scene.textures_path = bpy.props.StringProperty(
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
    del bpy.types.Scene.textures_path
    del bpy.types.Scene.output_path

    for c in classes:
        bpy.utils.unregister_class(c)

