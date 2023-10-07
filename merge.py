from utils.reflection import get_config
from PIL import Image
import os, random, itertools
import numpy as np


class Merge:
    
    def __init__(self, arguments: dict):
        print(f"{'='*20}init{'='*20}")
        self.args = arguments
        self.save_dir_split = self.args.get('save_dir_split')
        self.original_image_name = self.args.get('input_image_name')
        self.row_num = self.args.get('row_num')
        self.col_num = self.args.get('col_num')
        self.save_dir_merge = self.args.get('save_dir_merge')
        self.list_img_seq = []
        self.width = max(self.row_num, self.col_num)
        self.height = min(self.row_num, self.col_num)
        self.single_img_shape = None
        self.single_row_shape = None
        print(f"arguments: {args}")
        

    def run(self):
        print(f"{'='*20}run{'='*20}")
        
        # load the sub images
        self.splited_images = []
        for f in os.listdir(self.save_dir_split):
            tmp_img = Image.open(os.path.join(self.save_dir_split, f))
            tmp_img = np.array(tmp_img)
            self.splited_images.append(tmp_img)
        random.shuffle(self.splited_images)
        self.single_img_shape = self.splited_images[-1].shape
        
        # check the save folder
        if not os.path.exists(self.save_dir_merge):
            os.mkdir(self.save_dir_merge)
        for f in os.listdir(self.save_dir_merge):
            os.remove(os.path.join(self.save_dir_merge, f))
        
        # merge the sub images and save the result
        print("processing...\n")
        tfs = ["fliplr", "flipud", "rot90", None, None, None]
        ps = itertools.permutations(tfs, 3)
        self.tfs_list = list(set(ps))
        
        total = len(self.splited_images)
        print('merge_h 1')
        self.list_img_seq.append(self.merge_h(self.width))
        print(f'left sub-images: {len(self.splited_images)}/{total}')
        for _ in range(self.height-1):
            print(f'merge_h {_+2}')
            self.list_img_seq.append(self.merge_h(self.width))
            print(f'left sub-images: {len(self.splited_images)}/{total}')
        random.shuffle(self.list_img_seq)
        merged_img = self.merge_v(self.height)
        print(f"\nestimated image size: {merged_img.shape}")
        
        merged_img = Image.fromarray(merged_img)
        image_name = f"reconstructed {os.path.split(self.original_image_name)[-1]}"
        image_path = os.path.join(self.save_dir_merge, image_name)
        merged_img.save(image_path)
        print("\nDone!")

    
    def merge_h(self, length):
        '''concatenate sub-images horizontally'''
        width = length
        d1_list = []
        cnt = 1
        
        img_1 = self.splited_images[-1]
        if len(self.list_img_seq) != 0:
            for seq in self.tfs_list:
                for tf in seq:
                    if tf != None:
                        tmp_img = getattr(np, tf)(img_1)
                if self.single_img_shape == tmp_img.shape:
                    img_1 = tmp_img
                    break
                    
        img_right, img_left = img_1, img_1
        
        img_seq = []
        img_seq.append(img_1)

        for _ in range(width-1):
            min_d1 = np.inf
            index_k = None
            index_tf = None
            
            for k in range(len(self.splited_images[:-1])):
                for idx_tf, seq in enumerate(self.tfs_list):
                    img_k = self.splited_images[:-1][k]
                    for tf in seq:
                        if tf != None:
                            img_k = getattr(np, tf)(img_k)
                    if self.single_img_shape != img_k.shape:
                        continue

                    d1_left = np.mean(np.abs(img_left[:, 0] - img_k[:, -1]))
                    d1_right = np.mean(np.abs(img_right[:, -1] - img_k[:, 0]))
                    if d1_right > d1_left:
                        d1 = d1_left
                        rightward = False
                    else:
                        d1 = d1_right
                        rightward = True

                    if min_d1 > d1:
                        min_d1 = d1
                        index_k = k
                        index_tf = idx_tf

            img_k = self.splited_images[:-1][index_k]

            for tf in self.tfs_list[index_tf]:
                if tf != None:
                    img_k = getattr(np, tf)(img_k)

            if len(self.list_img_seq) == 0:
                if cnt != min(self.row_num, self.col_num):
                    d1_list.append(min_d1)
                    cnt += 1
                    if rightward:
                        img_seq.insert(-1, img_k)
                        img_right = img_k
                    else:
                        img_seq.insert(0, img_k)
                        img_left = img_k
                    del self.splited_images[index_k]
                elif cnt == min(self.row_num, self.col_num):
                    average_d1 = np.mean(np.array(d1_list))
                    if min_d1 > 2*average_d1: # this coefficient is a hyperparameter
                        self.width = min(self.row_num, self.col_num)
                        self.height = max(self.row_num, self.col_num)
                        
                        del self.splited_images[-1]
                        result = np.concatenate(img_seq, axis=1)
                        
                        if self.single_row_shape == None:
                            self.single_row_shape = result.shape
                        return result
                    else:
                        cnt += 1
                        if rightward:
                            img_seq.insert(-1, img_k)
                            img_right = img_k
                        else:
                            img_seq.insert(0, img_k)
                            img_left = img_k
                        del self.splited_images[index_k]
            else:
                if rightward:
                    img_seq.insert(-1, img_k)
                    img_right = img_k
                else:
                    img_seq.insert(0, img_k)
                    img_left = img_k
                del self.splited_images[index_k]
        
        del self.splited_images[-1]
        result = np.concatenate(img_seq, axis=1)
        
        if self.single_row_shape == None:
            self.single_row_shape = result.shape
        return result


    def merge_v(self, length):
        '''concatenate rows of sub-images vertically'''
        height = length
        
        img_1 = self.list_img_seq[-1]
        img_up, img_down = img_1, img_1
        
        img_rows = []
        img_rows.append(img_1)

        for _ in range(height-1):
            min_d1 = np.inf
            index_k = None
            index_tf = None
            for k in range(len(self.list_img_seq[:-1])):
                for idx_tf, seq in enumerate(self.tfs_list):
                    img_k = self.list_img_seq[:-1][k]
                    for tf in seq:
                        if tf != None:
                            img_k = getattr(np, tf)(img_k)
                    if self.single_row_shape != img_k.shape:
                        continue

                    d1_up = np.mean(np.abs(img_up[0, :] - img_k[-1, :]))
                    d1_down = np.mean(np.abs(img_down[-1, :] - img_k[0, :]))
                    if d1_up > d1_down:
                        d1 = d1_down
                        upward = False
                    else:
                        d1 = d1_up
                        upward = True

                    if min_d1 > d1:
                        min_d1 = d1
                        index_k = k
                        index_tf = idx_tf

            img_k = self.list_img_seq[:-1][index_k]

            for tf in self.tfs_list[index_tf]:
                if tf != None:
                    img_k = getattr(np, tf)(img_k)

            if upward:
                img_rows.insert(-1, img_k)
                img_up = img_k
            else:
                img_rows.insert(0, img_k)
                img_down = img_k
            del self.list_img_seq[index_k]
            
        del self.list_img_seq[-1]
        
        return np.concatenate(img_rows, axis=0)
                            
        
        
if __name__ == '__main__':
    
    argument_location = '.'.join(['tasks', 'arguments', 'config'])
    args = get_config(argument_location)
    
    process = Merge(args)
    process.run()