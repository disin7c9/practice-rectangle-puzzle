from utils.reflection import get_config
from PIL import Image
import os
import numpy as np


class Cut:
    
    def __init__(self, arguments: dict):
        print(f"{'='*30}init{'='*30}")
        self.args = arguments        
        self.input_image_name = self.args.get('input_image_name')
        self.ext = os.path.splitext(self.input_image_name)[-1]
        self.row_num = self.args.get('row_num')
        self.col_num = self.args.get('col_num')
        self.save_dir_split = self.args.get('save_dir_split')
        print(f"arguments: {self.args}")

    def run(self):
        print(f"{'='*30}run{'='*30}")
        
        # load the image
        img = Image.open(self.input_image_name)
        img = np.array(img)
        print(f"image size: {img.shape}")
        
        # dispose of the remainder
        shape_img = img.shape
        quotient_row, quotient_col = np.floor_divide(shape_img[:2], [self.row_num, self.col_num])
        mod_row, mod_col = np.remainder(shape_img[:2], [quotient_row, quotient_col])
        img = img[:shape_img[0]-mod_row, :shape_img[1]-mod_col]
        
        # split the image
        splited_img = self.cubify(img, [quotient_row, quotient_col, shape_img[-1]])
        
        # check the save folder
        if not os.path.exists(self.save_dir_split):
            os.mkdir(self.save_dir_split)
        for f in os.listdir(self.save_dir_split):
            os.remove(os.path.join(self.save_dir_split, f))
        
        # transform and save the sub-images
        print("processing...\n")
        for i in range(len(splited_img)):
            print(f"sub image: {i+1}/{len(splited_img)}")

            temp_img = splited_img[i]
            temp_img = self.transform(temp_img)
            temp_img = Image.fromarray(temp_img)
            
            sub_image_serial = "".join(str(k) for k in [np.random.randint(0,10) for i in range(10)])
            sub_image_name = "".join([sub_image_serial, self.ext])
            sub_image_path = os.path.join(self.save_dir_split, sub_image_name)
            
            temp_img.save(sub_image_path)
        print("\nDone!")

    
    def cubify(self, arr, newshape: list):
        '''Ref: https://stackoverflow.com/questions/42297115'''
        
        oldshape = np.array(arr.shape)
        newshape = np.array(newshape)
        repeats = (oldshape / newshape).astype(int)
        tmpshape = np.column_stack([repeats, newshape]).ravel()
        order = np.arange(len(tmpshape))
        order = np.concatenate([order[::2], order[1::2]])
        # newshape must divide oldshape evenly or else ValueError will be raised
        return arr.reshape(tmpshape).transpose(order).reshape(-1, *newshape)
        
        
    def transform(self, img):
        tfs = np.array(["fliplr", "flipud", "rot90"])
        bool_filter = np.random.choice([True, False], size=len(tfs), replace=True)
        tfs = tfs[bool_filter]
        np.random.shuffle(tfs)
        for tf in tfs:
            if tf == "rot90":
                img = getattr(np, tf)(img, 3)
            else:
                img = getattr(np, tf)(img)
        return img
    

    
if __name__ == '__main__':
    
    argument_location = '.'.join(['tasks', 'arguments', 'config'])
    args = get_config(argument_location)
    
    process = Cut(args)
    process.run()