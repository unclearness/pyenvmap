import pyenvmap as pem
import tkinter as tk
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import HORIZONTAL
from PIL import Image, ImageTk
import cv2
import numpy as np

if __name__ == '__main__':

    #=============#
    # Create root #
    #=============#
    root = tk.Tk()
    root.title("Image Show")
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
    #==============#
    # Make img src #
    #==============#
    # Read image
    src_path = "./data/studio_small_09_4k.exr"
    src_path = "./data/color.png"
    img_bgr = cv2.imread(src_path, -1)[..., :3]
    img_bgr_org = img_bgr.copy()
    # img_bgr = (img_bgr - np.min(img_bgr) /
    #           np.max(img_bgr) - np.min(img_bgr)) * 255
    img_bgr = np.clip(img_bgr, 0, 255).astype(np.uint8)

    view_img_width = 640
    view_img_height = int(img_bgr.shape[0] / img_bgr.shape[1] * view_img_width)
    img_bgr = cv2.resize(img_bgr, (view_img_width, view_img_height))
    img_bgr_start = img_bgr.copy()
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
        rotated = pem.rotateByEularXYZ(img_bgr_start, x, y, z)
        rotated_tk = formatConverter(rotated)
        imgCVT.configure(image=rotated_tk)
        label_val1.configure(text=x)
        label_val2.configure(text=y)
        label_val3.configure(text=z)

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

    #========#
    # Layout #
    #========#
    frmL.pack(side='left')
    frmC.pack(side='left')
    frmR.pack(side='left')
    imgORG.pack(side='top')
    label_imgORG.pack(side='top')
    imgCVT.pack(side='top')
    label_imgCVT.pack(side='top')
    scale1.pack(side='top')
    label_val1.pack(side='top')
    scale2.pack(side='top')
    label_val2.pack(side='top')
    scale3.pack(side='top')
    label_val3.pack(side='top')
    root.mainloop()
