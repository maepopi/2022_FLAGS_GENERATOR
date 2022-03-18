bl_info = {
    "name": "Flag Generator",
    "blender" : (3,0,0),
    "category": "Object",
    "location" : "View 3D",
    "description" : "Addon which generates and exports 3d flags",
    "author" : "Dr. Jusseaux <maelys.jusseaux@gmail.com>",
    "version":(1,0)
}


from email.mime import image
import pathlib
import os
from pydoc import visiblename
import shutil
import bpy
import glob
import subprocess


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
        basic_ratio = 1.5
        

        # Clean any potential orphan images
        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)

        
        SetupRenderSettings(main_scene)

        # Declare Resources path
        input_path = context.scene.input_path
        output_path = context.scene.output_path
        this_script_folder = os.path.dirname(os.path.realpath(__file__))

        #Todo : backup folder duplicate context.scene.input_path => nomdossier_backup => prévoir overwrite if existing dir/path. Comme ça c'est déjà sauvegardé. 
        Backup(this_script_folder, input_path)

        subfolders = os.listdir(input_path)
        # texture_path = None
        # name = None

        
        
        #Prepare compositor
        PrepareCompositor(main_scene, output_path)

        for folder in subfolders:
            #Get the subfolder name
            subfolder_name = folder
            #Get the subfolder path
            subfolder_path = os.path.join(input_path, folder)

            #Scale the flag according to new ratio
            ScaleFlag(subfolder_name, basic_ratio, flag_model)

            #Get the textures list
            textures_list = GetTextures(subfolder_path)
            print("Hey ! At this step, textures-list length is " + str(len(textures_list)))


            # # For each item in textures_list:
            for item in textures_list:
                print ("Texture is " + str(item))
                texture_path = os.path.join(subfolder_path, item)
                print ("Texture path is " + str(texture_path))
                texture_fullname = os.path.basename(texture_path)
                texture_name = os.path.splitext(texture_fullname)[0]
                print("Texture fullname is " + texture_fullname)
                print("Texture name is " + texture_name)

                # Normalize the image
                Normalize(texture_path, texture_fullname, texture_name)

                # Load and apply texture
                PlugTexture(main_scene, texture_path)

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
        col.prop(context.scene, "input_path")

        # Output path
        col = layout.column()
        col.prop(context.scene, "output_path")

        # Generate
        col = layout.column()
        col.operator("generate.generate_flags")

        
        

# FUNCTIONS
def SetupRenderSettings(scene):
    #   Create and place the camera
    # bpy.ops.object.camera_add(align='VIEW')
    # bpy.ops.view3d.camera_to_view()

    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.film_transparent = True

def Backup(script_folder, images_path):
    #Create the backup folder
    dst_path = os.path.join(script_folder, 'Backup')
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    
    #Copy paste the input folder there
    shutil.copytree(images_path, dst_path)



def ScaleFlag(name, basic_ratio, model):
    new_ratio = float(name)
    model.scale.x = new_ratio / basic_ratio

def GetTextures(subfolder_path):
    texture_list = []
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif']

    for extension in image_extensions:
        texture_list.extend(glob.glob(os.path.join(subfolder_path, extension)))

    return texture_list


def Normalize(script_folder, texture_path, texture_fullname, texture_name):
    ffmpeg_path = os.path.join(script_folder, 'ffmpeg', 'bin', 'ffmpeg.exe')
    outpath = os.path.join(texture_path, texture_name + 'reduced_converted' + '.jpg')
    resolution = 512

    #Here we define the four arguments we want to give the ffmpeg command. They will be written in a text file which will be saved as a "bat" file and launched by Python. We are asking Python to write the bat file for us.
    ffmpeg_command=[
        # The command we need is ffmpeg -i input_image -vf scale=512:512 output_image
        ffmpeg_path,
        "-i " + texture_path,
        "-vf scale=" + str(resolution) + ":" + str(resolution),
        outpath
    ]

    #Now we actually write the bat file. For each image, it's going to write a bat file with the command line defined in ffmpeg_command
    bat_file = open(script_folder + '\\normalizer' + texture_name + '.bat', 'w')
    for line in ffmpeg_command:
        bat_file.write(line)
        #Here we define that the separation between the four strings should be a space, because that's what the command prompt needs to call the ffmpeg command.
        bat_file.write(' ')
    bat_file.close()

    #Launch bat. The process_wait() makes sure that all the images are done.
    process = subprocess.Popen(script_folder + '\\normalizer' + texture_name +'.bat')
    process.wait()

    #Clean : delete the original file, rename the new one, and delete the bat file
    original_filepath = outpath
    new_filepath = os.path.join(texture_path, texture_name + '.jpg')
    os.remove(texture_path)
    os.rename(original_filepath, new_filepath)
    os.remove(script_folder + '\\normalizer' + texture_name +'.bat')



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


def PrepareCompositor(scene, path):
    bpy.context.area.ui_type = 'CompositorNodeTree'
    scene_tree = scene.node_tree
    links = scene_tree.links
    output_node = scene_tree.nodes["File Output"]
    output_node.base_path = path
    print("The output render path is " + str(path) )


def RenderFlag():
    bpy.ops.render.render(layer="ViewLayer", write_still=True)
    


def RenameThumbnail(output_path, name):
    original_folder = output_path
    print ("original folder at this step is " + str(original_folder))

    for item in os.listdir(original_folder):
        print("rename thumbnail name " + item)
        print("rename thumbnail original folder " + str(original_folder))
        original_filepath = os.path.join(original_folder, item)

        print("rename thumbnail original filepath is " + str(original_filepath))

        if 'Image' in item:
            # original_filepath = os.path.join(original_folder, item)
            original_name = os.path.splitext(item)[0]
            extension = os.path.splitext(item)[1]
            new_filepath = os.path.join(original_folder, name + extension)
            print("new file path is" + str(new_filepath))
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
    bpy.types.Scene.input_path = bpy.props.StringProperty(
        name = 'Input Folder',
        subtype = 'DIR_PATH',
    )

    bpy.types.Scene.output_path = bpy.props.StringProperty(
    name='Output Folder',
    subtype='DIR_PATH',
    )

    for c in classes:
        bpy.utils.register_class(c)



def unregister():
    del bpy.types.Scene.input_path
    del bpy.types.Scene.output_path

    for c in classes:
        bpy.utils.unregister_class(c)

