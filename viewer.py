import pyenvmap as pem
import tkinter as tk
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import HORIZONTAL
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

view_img_width = 640

if __name__ == '__main__':

    #=============#
    # Create root #
    #=============#
    root = tk.Tk()
    root.title("Envmap viewer")
    root.resizable(width=False, height=False)
    #===============#
    # Create frames #
    #===============#
    frmL = tk.Frame(root)
    frmC = tk.Frame(root)
    frmR = tk.Frame(root)
    #==================#
    # Define methods 1 #
    #==================#

    def formatConverter(img):
        # Convert to RGB format.
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Convert to PIL format.
        img_pil = Image.fromarray(img_rgb)
        # Convert to ImageTk format.
        img_tk = ImageTk.PhotoImage(img_pil)
        return img_tk

    def load(event=None):
        # Read image
        global img_bgr_org, img_bgr, org_ext, img_bgr_start, img_tk, c_img_tk
        src_path = load_path_ent.get()

        _, org_ext = os.path.splitext(src_path)
        if org_ext is None or len(org_ext) < 4:
            img_bgr = np.ones(
                (int(view_img_width / 2), view_img_width, 3), dtype=np.uint8) * 255
        else:
            img_bgr = cv2.imread(src_path, -1)
        img_bgr_org = img_bgr.copy()
        if org_ext.lower() in ['.exr', '.hdr']:
            # print(np.min(img_bgr, (0, 1)))
            img_bgr = (img_bgr - np.min(img_bgr, (0, 1)) /
                       np.max(img_bgr, (0, 1)) - np.min(img_bgr, (0, 1))) * 255
        img_bgr = np.clip(img_bgr, 0, 255).astype(np.uint8)

        view_img_height = int(
            img_bgr.shape[0] / img_bgr.shape[1] * view_img_width)
        img_bgr = cv2.resize(img_bgr, (view_img_width, view_img_height))
        img_bgr_start = img_bgr.copy()

        # For image processing
        img_tk = formatConverter(img_bgr)
        # For original image
        c_img_tk = formatConverter(img_bgr)

        imgORG.configure(image=img_tk)
        imgCVT.configure(image=c_img_tk)

    def save(event=None):
        x = val1.get()
        y = val2.get()
        z = val3.get()
        rotated = pem.rotateByEularXYZ(img_bgr_org, x, y, z)
        save_path = save_path_var.get()
        cv2.imwrite(save_path, rotated)

    #==============#
    # Make img src #
    #==============#

    img_bgr = np.ones(
        (int(view_img_width / 2), view_img_width, 3), dtype=np.uint8) * 255

    # For image processing
    img_tk = formatConverter(img_bgr)
    # For original image
    c_img_tk = formatConverter(img_bgr)
    #==================#
    # Define methods 2 #
    #==================#

    # Do not forget 'event=None', or an arg error occurs.
    def changeVal(event=None):
        global imgCVT, blur_tk, rotated_tk
        """
        size = 3 ** val1.get()
        sigma = val2.get()
        blur = cv2.GaussianBlur(img_bgr, (size, size), sigma)
        blur_tk = formatConverter(blur)
        imgCVT.configure(image=blur_tk)
        label_val1.configure(text=size)
        label_val2.configure(text=sigma)
        """
        x = val1.get()
        y = val2.get()
        z = val3.get()
        rotated, R = pem.rotateByEularXYZ(img_bgr_start, x, y, z)
        rotated_tk = formatConverter(rotated)
        imgCVT.configure(image=rotated_tk)
        label_val1.configure(text=x)
        label_val2.configure(text=y)
        label_val3.configure(text=z)
        R_text = ""
        for j in range(3):
            for i in range(3):
                pad = " " if R[i, j] >= 0 else ""
                R_text += (pad + '{:.5f}'.format(R[i, j]) + " ")
            R_text += '\n'
        # rot_val_var.set(R_text)
        text_box.insert('1.0', R_text)

    #    imgCVT.photo = blur_tk     #If you do not want "blur_tk" to be global val, activate this script instead.
    #    imgCVT.image = blur_tk     #This will work as well as above.
    #================#
    # Create widgets #
    #================#
    imgORG = tk.Label(frmL, image=c_img_tk)
    imgCVT = tk.Label(frmC, image=img_tk)
    val1 = tk.IntVar()
    scale1 = tk.Scale(
        frmR,
        variable=val1,
        from_=0,
        to=360,
        resolution=1,
        showvalue=0,
        label="Eular X",
        orient=tk.HORIZONTAL,
        command=changeVal
    )
    val2 = tk.IntVar()
    scale2 = tk.Scale(
        frmR,
        variable=val2,
        from_=0,
        to=360,
        resolution=1,
        showvalue=0,
        label="Eular Y",
        orient=tk.HORIZONTAL,
        command=changeVal
    )
    val3 = tk.IntVar()
    scale3 = tk.Scale(
        frmR,
        variable=val3,
        from_=0,
        to=360,
        resolution=1,
        showvalue=0,
        label="Eular Z",
        orient=tk.HORIZONTAL,
        command=changeVal
    )
    label_imgORG = tk.Label(frmL, text="Original image")
    label_imgCVT = tk.Label(frmC, text="Converted image")
    label_val1 = tk.Label(frmR, text="0")
    label_val2 = tk.Label(frmR, text="0")
    label_val3 = tk.Label(frmR, text="0")

    load_path_var = tk.StringVar(frmR)
    load_path_var.set("./data/studio_small_09_4k.exr")
    load_path_ent = tk.Entry(frmR, textvariable=load_path_var)

    load_text = tk.StringVar(frmR)
    load_text.set("Load")
    load_button = tk.Button(frmR, textvariable=load_text, command=load)

    load()

    #rot_val_var = tk.StringVar(frmR,)
    #rot_val_var.set("1 0 0\n0 1 0\n0 0 1\n")
    #rot_val_ent = tk.Entry(frmR, textvariable=rot_val_var,)

    text_box = tk.Text(height=3, width=30)

    save_path_var = tk.StringVar(frmR)
    save_path_var.set("./out" + org_ext)
    save_path_ent = tk.Entry(frmR, textvariable=save_path_var)

    save_text = tk.StringVar(frmR)
    save_text.set("Save")
    save_button = tk.Button(frmR, textvariable=save_text, command=save)

    #========#
    # Layout #
    #========#
    frmL.pack(side='top')
    frmC.pack(side='top')
    frmR.pack(side='left')

    imgORG.pack(side='top')
    label_imgORG.pack(side='top')
    imgCVT.pack(side='top')
    label_imgCVT.pack(side='top')

    load_path_ent.pack(side='top')
    load_button.pack(side='top')
    scale1.pack(side='top')
    label_val1.pack(side='top')
    scale2.pack(side='top')
    label_val2.pack(side='top')
    scale3.pack(side='top')
    text_box.pack(side='top')
    # rot_val_ent.pack(side='top')
    label_val3.pack(side='top')
    save_path_ent.pack(side='top')
    save_button.pack(side='top')

    root.mainloop()
