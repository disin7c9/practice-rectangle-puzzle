import os

main_dir = os.path.dirname(
    os.path.abspath('__main__')
)

config = dict(
    input_image_name = os.path.join(main_dir, "Saint_Remy\\Starry Night.jpg"),
    save_dir_split = os.path.join(main_dir, "splited_images"),
    save_dir_merge = os.path.join(main_dir, "merged_image"),
    row_num = 3,
    col_num = 3,
)