# opencv_perspective_corrector_gui
Simple scripts (or set of scripts) to process a query of images with different perspective to fix manually made timelapse.

Just in case leaving description of GUI.
1. Specify folder with images in Config.py
2. Copy in that folder a pack of "timelapse" frame images made by hand. Thus poorly overlapping.
3.1 Run CloseImageCorrection.py script. It would open images one by one in opencv's GUI.
3.2 Using mouse wheel press set or correct possitions for guidelines over image.
3.3 Try to match them with some notable "almost straight" lines.
3.4 Afterwards just press any key.
4. When done - script would generate .log file in images direcory. This file contains images paths and coordinates of it's perspective reference points
4.1 Thus it's easy to concatenate result with new images, or fix ones of original set. Just process them in different folder and merge with main set (by hand, or with simple scripting).
5. Just run Processor.py and in target directory would be generated a set of images corrected to average perspective of all images listed in .log file.
