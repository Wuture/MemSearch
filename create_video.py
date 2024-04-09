import cv2
import os
from natsort import natsorted
from moviepy.editor import VideoFileClip, concatenate_videoclips

# get date 
from datetime import datetime

def create_video_from_images(images, output_folder, video_name, fps=1):
    # Determine video dimensions from the first image (assuming all images are the same size)
    frame = cv2.imread(images[0])

    # print (images[0])

    # get frame size
    frame_size = (frame.shape[1], frame.shape[0])
    # print (images[0])
  
    # Create video writer
    # video_path = os.path.join(output_folder, f"{today}/{video_name}.mp4")
    # check if today folder exists
    today = datetime.now().date()
    if not os.path.exists(output_folder + str(today)):
        os.makedirs(output_folder + str(today))
    video_path = os.path.join(output_folder + str(today), f"{video_name}.mp4") 

    print (video_path)
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, frame_size)
    
    for image_path in images:
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Skipped a missing or corrupt image: {image_path}")
            continue
        out.write(frame)
    
    out.release()
    print(f"Video created: {video_path}")

def group_and_create_videos(image_folder, output_folder, fps=1):
        # Create a list to keep track of groups
    # all_images = natsorted(glob.glob(f"{image_folder}/*.jpg"))
    # print (all_images) one by one
    all_images = os.listdir(image_folder)
    all_images.sort(key=lambda x: os.path.getctime(os.path.join(image_folder, x)))

    current_app = None
    current_group = []
    video_index = 0  # A simple index to ensure unique video names

    for image_path in all_images:

        app_name = os.path.basename(image_path).split('_')[0]
        
        # Start a new group if the application name changes
        if app_name != current_app:
            if current_group:
                video_name = f"{current_app}_{video_index}"
                create_video_from_images(current_group, output_folder, video_name, fps)
                video_index += 1
            current_app = app_name
            current_group = []

        current_group.append(image_folder + image_path)

    # Handle the last group if exists
    if current_group:
        video_name = f"{current_app}_{video_index}"
        create_video_from_images(current_group, output_folder, video_name, fps)


if __name__ == "__main__":
    # print ("hello world")

    today = datetime.now().date()
    # Usage example
    # image folder is entire_screenshot
    # output folder is output_videos
    image_folder = 'entire_screenshot/'  # Update this to the folder containing your images
    output_folder = 'output_videos/'  # Update this to where you want your videos saved

    # if output folder does not exist, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    group_and_create_videos(image_folder, output_folder)

    # output_folder needs to be added with today's date
    output_folder = output_folder + str(today) + '/'

    # Now get the output videos from output_videos folder, and combine them into one video
    all_videos = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith('.mp4')]
    all_videos.sort(key=lambda x: os.path.getctime(x))

    # Create a list of VideoFileClip objects
    clips = [VideoFileClip(video) for video in all_videos]

    # Concatenate the video clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Specify the path for the combined video
    combined_video_path = os.path.join(output_folder, f"video_summary.mp4")

    # Write the final clip to the specified file
    final_clip.write_videofile(combined_video_path, codec="libx264", fps=24)

    # Release resources held by moviepy clips
    final_clip.close()
    for clip in clips:
        clip.close()

    print(f"Combined video created at {combined_video_path}")

