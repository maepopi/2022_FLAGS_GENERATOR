# Introduction

This is a small Blender addon I worked on a few years ago. It automatically generates 3D animated flags ready for AR/VR applications. To work, it needs an input folder with all the flag images, and a reference Blender scene from which you'll need to launch the addon. It's a rather old project, so the code would definitely need a bit of cleanup.

# Installation

1. Download and install Blender 3.0.1
2. Clone this repo
3. In the repo, you'll see a blender scene. Open that scene with Blender 3.0.1
4. Install the addon by going to Preferences / addons, and select the **flag_generator.py** script. Click install. Now you'll see a panel with the name of your addon on the right window.


# Usage
1. You will first need to download the flags you want. I recommend scrapping them on a website such as [Worldometer](https://www.worldometers.info/geography/flags-of-the-world/) (If you are interested I can develop a scrapping script on purpose, just reach out to me and I'll see what I can do). Note their ratio (very important, you can find this easily on Wikipedia), and put the image of the flag in a folder named with the ratio ('1.5', '2.3' etc).
2. In Blender, click on the **Input** form, and copy paste the path to your input folder.
3. In Blender, click on the **Output** form, and copy paste the path to your output folder.


> Note
>
> Flags have different ratios, that is why I designed my script to apply the right scale depending on the name of the folder your flag image is in. For instance the flag of Libya is 2.3, so you'll have to put it in a subfolder named '2.3', inside the 'Input' folder. 
> There's an exception for logos though. If you want to generate a flag of a logo, put your logo image into a folder named "Logo". If the script sees the word "Logo", it will automatically set a scale to 1.